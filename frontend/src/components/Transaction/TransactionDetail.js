import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getTransactionDetail, deleteTransaction } from '../../api/transaction';

const TransactionDetail = () => {
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState(null);
  const { id } = useParams();

  const handleDelete = async () => {
    await deleteTransaction(transaction.id);
      navigate("/"); //TODO
  };

  useEffect(() => {
    const getTransaction = async () => {
      const response = await getTransactionDetail(id);
      setTransaction(response);
    };

    getTransaction();
  }, [id]);

  return transaction ? (
    <div>
      <h2>{transaction.title}</h2>
      <p>{transaction.description}</p>
      <button onClick={handleDelete}>Delete Transaction</button>
      {/* Render other transaction properties */}
    </div>
  ) : (
    <p>Loading...</p>
  );
};

export default TransactionDetail;
