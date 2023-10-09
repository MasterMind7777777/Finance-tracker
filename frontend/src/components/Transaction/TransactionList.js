import React, { useEffect, useState } from 'react';
import { getTransactionList } from '../../api/transaction';
import AuthService from '../../services/authService';
import ListRenderer from '../Common/Lists/ListBase';

const TransactionList = () => {
  const [transactions, setTransactions] = useState([]);
  const [transactionTitles, setTransactionTitles] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      getTransactionList(token)
        .then((data) => {
          setTransactions(data);
          // Generate titles for each transaction, this could be anything based on your needs
          console.log(transactions);
          const titles = data.map(
            (transaction) => `Transaction: ${transaction.title}`,
          );
          setTransactionTitles(titles);
        })
        .catch((err) => console.error(err));
    }
  }, []);

  const contentConfig = {
    title: 'title',
    paragraphs: [
      { key: 'amount', label: 'Amount' },
      { key: 'date', label: 'Date' },
      { key: 'category', label: 'Category' },
    ], // Now an array of objects
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
