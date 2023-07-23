import React, { useState, useEffect } from 'react';
import { assignCategory } from '../../api/transaction';

const AssignCategoryButton = ({ transactionId, refreshTransaction }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('Idle');

  useEffect(() => {
    if (isLoading) {
      fetchResult();
    }
  }, [isLoading]);

  const fetchResult = async () => {
    try {
      setStatus('Pending');
      const response = await assignCategory(transactionId);

      if (response.status === 'Complete') {
        setStatus('Complete');
        setIsLoading(false);
        refreshTransaction();
      } else if (response.status === 'Pending') {
        // If the status is 'Pending', fetch the result again after a short delay
        const delay = setTimeout(() => {
          fetchResult();
          clearTimeout(delay);
        }, 500); // You can adjust the delay time (in milliseconds) as needed
      }
    } catch (error) {
      console.error(error);
      setStatus('Error');
      setIsLoading(false);
    }
  };

  const handleAssignCategory = () => {
    setIsLoading(true);
  };

  return (
    <div>
      <button onClick={handleAssignCategory} disabled={isLoading}>
        {isLoading ? 'Assigning...' : 'Assign Category'}
      </button>
    </div>
  );
};

export default AssignCategoryButton;
