import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getTransactionDetail, deleteTransaction } from '../../api/transaction';
import AssignCategoryButton from '../Category/AssignCategoryButton';
// TODO Add update button
const TransactionDetailParent = () => {
  const [transaction, setTransaction] = useState(null);
  const { id } = useParams();
  
  const refreshTransaction = async () => {
    const response = await getTransactionDetail(id);
    setTransaction(response);
  }

  useEffect(() => {
    refreshTransaction();
  }, [id]);

  return transaction ? (
    <div>
      <TransactionDetail transaction={transaction} refreshTransaction={refreshTransaction} />
      <AssignCategoryButton transactionId={transaction.id} refreshTransaction={refreshTransaction} />
    </div>
  ) : (
    <p>Loading...</p>
  );
};

const TransactionDetail = ({transaction, refreshTransaction}) => {
  const navigate = useNavigate();
  
  const handleDelete = async () => {
    await deleteTransaction(transaction.id);
    navigate("/transactions");
  };
  return (
    <div>
      <h2>{transaction.title}</h2>
      <p>Category: {transaction.category_name || "None"}</p> {/* display category name or 'None' */}  
      <p>Amount: {transaction.amount} {transaction.currency}</p>
      <p>Description: {transaction.description}</p>
      <button onClick={handleDelete}>Delete Transaction</button>
      {/* Render other transaction properties */}
    </div>
  );
};

export default TransactionDetailParent;
