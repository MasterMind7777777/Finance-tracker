import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { assignCategory } from '../../api/transaction';
import { ActionElementType } from '../Common/constants/actionElementType';
import { TaskStatus } from '../Common/constants/StatusCodes'; // Import your TaskStatus object

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
      const response = await assignCategory(transactionId);
      if (response.status === TaskStatus.COMPLETE) {
        // Use TaskStatus.COMPLETE
        setStatus(TaskStatus.COMPLETE); // Use TaskStatus.COMPLETE
        refreshTransaction();
      } else if (response.status === TaskStatus.PENDING) {
        // Use TaskStatus.PENDING
        setTimeout(fetchResult, 500);
      }
    } catch (err) {
      setStatus(TaskStatus.ERROR); // Use TaskStatus.ERROR
      setError(err.message);
    }
  };

  useEffect(() => {
    setStatus(null); // Use TaskStatus.PENDING
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
        disabled: status === TaskStatus.PENDING, // Use TaskStatus.PENDING
        label:
          status === TaskStatus.PENDING ? 'Assigning...' : 'Assign Category', // Use TaskStatus.PENDING
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
