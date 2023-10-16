import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getTransactionDetail, deleteTransaction } from '../../api/transaction';
import AssignCategoryButton from '../Category/AssignCategoryButton';
// import PropTypes from 'prop-types';
import SplitTransactionForm from './SplitTransactionForm';
import { DetailComponent } from '../Common/Detail/DetailBase'; // Import generalized DetailComponent
import { logMessage } from '../../api/loging';

const TransactionDetailParent = () => {
  const [transaction, setTransaction] = useState(null);
  const { id } = useParams();

  const refreshTransaction = async () => {
    logMessage(
      'info',
      'Fetching transaction details.',
      'TransactionDetailParent',
    );
    const response = await getTransactionDetail(id);
    setTransaction(response);
  };

  const detailFields = [
    { key: 'title', label: 'Transaction Title' },
    { key: 'category_name', label: 'Category' },
    { key: 'amount', label: 'Amount' },
    { key: 'currency', label: 'Currency' },
    { key: 'description', label: 'Description' },
  ];

  const handleDeleteAction = async () => {
    logMessage(
      'info',
      `Deleting transaction with ID: ${id}`,
      'TransactionDetailParent',
    );
    await deleteTransaction(id);
  };

  const actionConfigs = [
    {
      type: 'button',
      Component: {
        label: 'Delete',
        execute: handleDeleteAction,
        navigate: '/transactions',
      },
    },
    {
      type: 'element',
      Component: AssignCategoryButton,
      props: { transactionId: id, refreshTransaction },
    },
    {
      type: 'element',
      Component: SplitTransactionForm,
      props: { transactionId: id },
    },
  ];

  useEffect(() => {
    logMessage(
      'info',
      'TransactionDetailParent component mounted.',
      'TransactionDetailParent',
    );
    refreshTransaction();
  }, [id]);

  return transaction ? (
    <div>
      <DetailComponent
        entityTitle="Transaction information"
        fetchDetail={getTransactionDetail}
        detailFields={detailFields}
        actionConfigs={actionConfigs}
      />
    </div>
  ) : (
    <p>Loading...</p>
  );
};

export default TransactionDetailParent;
