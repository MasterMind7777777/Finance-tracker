import React, { useEffect, useState } from 'react';
import { getTransactionList } from '../../api/transaction';
import AuthService from '../../services/authService';
import ListRenderer from '../Common/Lists/ListBase';
import { logMessage } from '../../api/loging';

const TransactionList = () => {
  const [transactions, setTransactions] = useState([]);
  const [transactionTitles, setTransactionTitles] = useState([]);

  useEffect(() => {
    logMessage('info', 'TransactionList component mounted.', 'TransactionList');
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      logMessage(
        'info',
        'Attempting to fetch transaction list.',
        'TransactionList',
      );
      getTransactionList(token)
        .then((data) => {
          setTransactions(data);
          logMessage(
            'info',
            `Fetched ${data.length} transactions.`,
            'TransactionList',
          );
          // Generate titles for each transaction
          const titles = data.map(
            (transaction) => `Transaction: ${transaction.title}`,
          );
          setTransactionTitles(titles);
        })
        .catch((err) => {
          logMessage(
            'error',
            `Error fetching transactions: ${err.message}`,
            'TransactionList',
          );
          console.error(err);
        });
    } else {
      logMessage(
        'warning',
        'No authentication token found.',
        'TransactionList',
      );
    }
  }, []);

  const contentConfig = {
    title: 'title',
    paragraphs: [
      { key: 'amount', label: 'Amount' },
      { key: 'date', label: 'Date' },
      { key: 'category', label: 'Category' },
    ],
    links: [
      { link: 'id', linkPrefix: '/transactions/', linkText: 'View Details' },
    ],
  };

  return (
    <ListRenderer
      items={transactions}
      itemTitles={transactionTitles}
      keyExtractor={(item) => item.id}
      title="Transaction List"
      contentConfig={contentConfig}
    />
  );
};

export default TransactionList;
