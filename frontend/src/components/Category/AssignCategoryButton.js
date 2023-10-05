import React, { useState, useEffect } from 'react';
import { assignCategory } from '../../api/transaction';
import PropTypes from 'prop-types';

const AssignCategoryButton = ({ transactionId, refreshTransaction }) => {
  const [shouldFetchResult, setShouldFetchResult] = useState(false);
  const [status, setStatus] = useState('NOT_STARTED');

  useEffect(() => {
    let isActive = true;

    const fetchResult = async () => {
      try {
        setStatus('IN_PROGRESS');
        const response = await assignCategory(transactionId);

        if (isActive && response.status === 'COMPLETED') {
          setStatus('COMPLETED');
          setShouldFetchResult(false);
          refreshTransaction();
        } else if (isActive && response.status === 'IN_PROGRESS') {
          const delay = setTimeout(() => {
            if (isActive) fetchResult();
            clearTimeout(delay);
          }, 500);
        }
      } catch (error) {
        console.error(error);
        setStatus('FAILED');
        setShouldFetchResult(false);
      }
    };

    if (shouldFetchResult) {
      fetchResult();
    }

    return () => {
      isActive = false;
    };
  }, [shouldFetchResult, transactionId, refreshTransaction]);

  const handleAssignCategory = () => {
    setShouldFetchResult(true);
  };

  return (
    <div>
      <button onClick={handleAssignCategory} disabled={shouldFetchResult}>
        {shouldFetchResult ? 'Assigning...' : 'Assign Category'}
      </button>
      <p>Status: {status}</p>
    </div>
  );
};

AssignCategoryButton.propTypes = {
  transactionId: PropTypes.string.isRequired,
  refreshTransaction: PropTypes.func.isRequired,
};

export default AssignCategoryButton;
