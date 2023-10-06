import React, { useState, useEffect } from 'react';
import { assignCategory } from '../../api/transaction';
import PropTypes from 'prop-types';

const AssignCategoryButton = ({ transactionId, refreshTransaction }) => {
  const [status, setStatus] = useState('NOT_STARTED');
  const [error, setError] = useState(null);

  const fetchResult = async () => {
    console.log('fetchResult called'); // Debug log
    try {
      setStatus('IN_PROGRESS');
      const response = await assignCategory(transactionId);
      console.log('Response received:', response); // Debug log

      if (response.status === 'Complete') {
        console.log('Status completed'); // Debug log
        setStatus('COMPLETED');
        refreshTransaction();
      } else if (response.status === 'Pending') {
        // Updated this line
        console.log('Status pending, retrying...'); // Updated this line
        // Re-call fetchResult after a delay if the status is 'Pending'
        setTimeout(fetchResult, 500);
      }
    } catch (error) {
      console.error(error);
      setStatus('FAILED');
      setError(error.message);
    }
  };

  useEffect(() => {
    console.log('useEffect - transactionId changed'); // Debug log
    setStatus('NOT_STARTED'); // Reset status when transactionId changes
    setError(null); // Reset error when transactionId changes
  }, [transactionId]);

  const handleAssignCategory = () => {
    console.log('handleAssignCategory called'); // Debug log
    fetchResult(); // Call fetchResult directly here
  };

  return (
    <div>
      <button
        onClick={handleAssignCategory}
        disabled={status === 'IN_PROGRESS'}
      >
        {status === 'IN_PROGRESS' ? 'Assigning...' : 'Assign Category'}
      </button>
      <p>Status: {status}</p>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
};

AssignCategoryButton.propTypes = {
  transactionId: PropTypes.number.isRequired,
  refreshTransaction: PropTypes.func.isRequired,
};

export default AssignCategoryButton;
