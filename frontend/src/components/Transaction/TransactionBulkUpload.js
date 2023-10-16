import React, { useState } from 'react';
import { bulkUploadTransactions } from '../../api/transaction';
import { toast } from 'react-toastify';
import ActionsSection from '../Common/Actions';
import FileInputComponent from '../Common/Forms/FileUpload';
import { TaskStatus } from '../Common/constants/StatusCodes';
import { logMessage } from '../../api/loging';

const TransactionBulkUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const fileUploadHandler = async () => {
    logMessage('info', 'Initiating bulk upload.', 'TransactionBulkUpload');
    if (!selectedFile) {
      logMessage(
        'warn',
        'No file selected for bulk upload.',
        'TransactionBulkUpload',
      );
      toast.error('No file selected!');
      return;
    }

    try {
      let response = await bulkUploadTransactions(selectedFile);
      logMessage(
        'info',
        'Bulk upload API response received.',
        'TransactionBulkUpload',
      );

      if (typeof response === 'object' && response.status) {
        switch (response.status) {
          case TaskStatus.PENDING:
            logMessage('info', 'Bulk upload pending.', 'TransactionBulkUpload');
            toast.info(
              'Upload successful, transactions are being processed...',
            );
            break;
          case TaskStatus.ERROR:
            logMessage(
              'error',
              `Bulk upload failed: ${response.message}`,
              'TransactionBulkUpload',
            );
            toast.error(`Upload failed: ${response.message}`);
            break;
          case TaskStatus.COMPLETE:
            logMessage(
              'success',
              `Bulk upload complete: ${response.message}`,
              'TransactionBulkUpload',
            );
            toast.success(response.message);
            return;
          default:
            logMessage(
              'error',
              'Unexpected status received during bulk upload.',
              'TransactionBulkUpload',
            );
            toast.error('Unexpected status received. Please try again.');
            break;
        }
      } else {
        logMessage(
          'error',
          'Upload failed due to unknown reasons.',
          'TransactionBulkUpload',
        );
        toast.error('Upload failed. Please try again.');
        return;
      }

      const intervalId = setInterval(async () => {
        response = await bulkUploadTransactions(selectedFile);
        logMessage(
          'info',
          'Checking bulk upload status.',
          'TransactionBulkUpload',
        );

        if (response.status === TaskStatus.COMPLETE) {
          clearInterval(intervalId);
          logMessage(
            'success',
            `Bulk upload complete: ${response.message}`,
            'TransactionBulkUpload',
          );
          toast.success(response.message);
        }
      }, 5000);
    } catch (error) {
      logMessage(
        'error',
        `Bulk upload encountered an error: ${error.message}`,
        'TransactionBulkUpload',
      );
      toast.error(`An error occurred: ${error.message}`);
    }
  };

  const handleFileChange = (file) => {
    if (file) {
      setSelectedFile(file);
    }
  };

  const actionConfigs = [
    {
      type: 'element',
      Component: FileInputComponent,
      props: { refreshFile: handleFileChange },
    },
    {
      type: 'button',
      Component: {
        label: 'Upload',
        action: fileUploadHandler,
      },
    },
  ];

  const executeAction = (Component) => {
    if (Component.action) {
      Component.action();
    }
  };

  return (
    <div>
      <ActionsSection
        actionConfigs={actionConfigs}
        executeAction={executeAction}
      />
    </div>
  );
};

export default TransactionBulkUpload;
