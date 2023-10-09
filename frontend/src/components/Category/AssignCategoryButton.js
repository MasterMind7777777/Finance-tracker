import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { assignCategory } from '../../api/transaction';
import { ActionElementType } from '../Common/constants/actionElementType';

const AssignCategoryButton = ({
  transactionId,
  refreshTransaction,
  children,
}) => {
  const [status, setStatus] = useState('NOT_STARTED');
  const [error, setError] = useState(null);

  const fetchResult = async () => {
    try {
      setStatus('IN_PROGRESS');
      const response = await assignCategory(transactionId);
      if (response.status === 'Complete') {
        setStatus('COMPLETED');
        refreshTransaction();
      } else if (response.status === 'Pending') {
        setTimeout(fetchResult, 500);
      }
    } catch (err) {
      setStatus('FAILED');
      setError(err.message);
    }
  };

  useEffect(() => {
    setStatus('NOT_STARTED');
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
        disabled: status === 'IN_PROGRESS',
        label: status === 'IN_PROGRESS' ? 'Assigning...' : 'Assign Category',
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
