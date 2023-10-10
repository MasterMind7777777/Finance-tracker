import React, { useState } from 'react';
import { bulkUploadTransactions } from '../../api/transaction';
import { toast } from 'react-toastify';
import ActionsSection from '../Common/Actions';
import FileInputComponent from '../Common/Forms/FileUpload';
import { TaskStatus } from '../Common/constants/StatusCodes';

const TransactionBulkUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const fileUploadHandler = async () => {
    if (!selectedFile) {
      toast.error('No file selected!');
      return;
    }

    try {
      let response = await bulkUploadTransactions(selectedFile);
      console.log(response);

      if (typeof response === 'object' && response.status) {
        switch (response.status) {
          case TaskStatus.PENDING:
            toast.info(
              'Upload successful, transactions are being processed...',
            );
            break;
          case TaskStatus.ERROR:
            toast.error(`Upload failed: ${response.message}`);
            break;
          case TaskStatus.COMPLETE:
            toast.success(response.message);
            return;
          default:
            toast.error('Unexpected status received. Please try again.');
            break;
        }
      } else {
        toast.error('Upload failed. Please try again.');
        return;
      }

      const intervalId = setInterval(async () => {
        response = await bulkUploadTransactions(selectedFile); // Function to check status needs to be implemented
        console.log(response);

        if (response.status === TaskStatus.COMPLETE) {
          clearInterval(intervalId);
          toast.success(response.message);
        }
      }, 5000); // Changed from 200ms to 5000ms for checking status every 5 seconds
    } catch (error) {
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
