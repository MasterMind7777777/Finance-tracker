import React, { useState, useEffect } from 'react';
import {
  getSplitTransactions,
  acceptTransactionSplit,
  declineTransactionSplit,
} from '../../api/transaction';
import { logMessage } from '../../api/loging'; // Import logMessage function

const SplitTransactionList = () => {
  const [splitTransactions, setSplitTransactions] = useState([]);

  const fetchSplitTransactions = async () => {
    logMessage('info', 'Fetching split transactions.', 'SplitTransactionList');
    try {
      const response = await getSplitTransactions();
      console.log(response); // This can be removed after verification
      setSplitTransactions(response);
      logMessage(
        'info',
        'Fetched split transactions successfully.',
        'SplitTransactionList',
      );
    } catch (error) {
      logMessage(
        'error',
        `Failed fetching split transactions: ${error.message}`,
        'SplitTransactionList',
      );
      console.error('Error fetching split transactions:', error); // Keep for additional local debugging
    }
  };

  useEffect(() => {
    fetchSplitTransactions(); // Call fetchSplitTransactions when the component mounts
  }, []); // Empty dependency array means this useEffect runs once, similar to componentDidMount

  const handleAccept = async (id) => {
    logMessage(
      'info',
      `Accepting split transaction ID: ${id}`,
      'SplitTransactionList',
    );
    await acceptTransactionSplit(id);
    fetchSplitTransactions(); // refresh the list
  };

  const handleDecline = async (id) => {
    logMessage(
      'info',
      `Declining split transaction ID: ${id}`,
      'SplitTransactionList',
    );
    await declineTransactionSplit(id);
    fetchSplitTransactions(); // refresh the list
  };

  return (
    <ul>
      {splitTransactions.map((split) => (
        <li key={split.id}>
          {split.transaction_title} - {split.status}
          {split.status === 'pending' && (
            <>
              <button onClick={() => handleAccept(split.id)}>Accept</button>
              <button onClick={() => handleDecline(split.id)}>Decline</button>
            </>
          )}
        </li>
      ))}
    </ul>
  );
};

export default SplitTransactionList;
