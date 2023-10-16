import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { assignCategory } from '../../api/transaction';
import { ActionElementType } from '../Common/constants/actionElementType';
import { TaskStatus } from '../Common/constants/StatusCodes'; // Import your TaskStatus object
import { logMessage } from '../../api/loging'; // Import centralized logging function

const AssignCategoryButton = ({
  transactionId,
  refreshTransaction,
  children,
}) => {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const fetchResult = async () => {
    try {
      setStatus(TaskStatus.PENDING); // Use TaskStatus.PENDING
      logMessage(
        'info',
        `Attempting to assign category for transactionId: ${transactionId}`,
        'AssignCategoryButton',
      );

      const response = await assignCategory(transactionId);
      if (response.status === TaskStatus.COMPLETE) {
        setStatus(TaskStatus.COMPLETE);
        refreshTransaction();
        logMessage(
          'info',
          `Successfully assigned category for transactionId: ${transactionId}`,
          'AssignCategoryButton',
        );
      } else if (response.status === TaskStatus.PENDING) {
        setTimeout(fetchResult, 500);
      }
    } catch (err) {
      setStatus(TaskStatus.ERROR);
      setError(err.message);
      logMessage(
        'error',
        `Failed to assign category for transactionId: ${transactionId}. Error: ${err.message}`,
        'AssignCategoryButton',
      );
    }
  };

  useEffect(() => {
    setStatus(null);
    setError(null);
  }, [transactionId]);

  const handleAssignCategory = () => {
    fetchResult();
  };

  const elements = [
    {
      type: ActionElementType.BUTTON,
      props: {
        onClick: handleAssignCategory,
        disabled: status === TaskStatus.PENDING,
        label:
          status === TaskStatus.PENDING ? 'Assigning...' : 'Assign Category',
      },
    },
    {
      type: ActionElementType.STATUS,
      props: { status },
    },
    {
      type: ActionElementType.Error,
      props: { error },
    },
  ];

  return children(elements);
};

AssignCategoryButton.propTypes = {
  transactionId: PropTypes.number.isRequired,
  refreshTransaction: PropTypes.func.isRequired,
  children: PropTypes.func.isRequired,
};

export default AssignCategoryButton;
