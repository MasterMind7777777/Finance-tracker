import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getTransactionDetail, deleteTransaction } from '../../api/transaction';
import AssignCategoryButton from '../Category/AssignCategoryButton';
// import PropTypes from 'prop-types';
import SplitTransactionForm from './SplitTransactionForm';
import { DetailComponent } from '../Common/Detail/DetailBase'; // Import generalized DetailComponent

const TransactionDetailParent = () => {
  const [transaction, setTransaction] = useState(null);
  const { id } = useParams();

  const refreshTransaction = async () => {
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
