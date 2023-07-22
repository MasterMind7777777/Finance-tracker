import React, { useState, useEffect } from 'react';
import { getTransactionList, updateTransaction } from '../../api/transaction';

const UpdateTransaction = ({ match }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  // Add states for other transaction fields

  useEffect(() => {
    const getTransaction = async () => {
      const transaction = await getTransactionList(match.params.id);
      setTitle(transaction.title);
      setDescription(transaction.description);
      // Set other fields...
    };

    getTransaction();
  }, [match.params.id]);

  const handleSubmit = async event => {
    event.preventDefault();

    const transaction = {
      title,
      description,
      // Other fields...
    };

    await updateTransaction(match.params.id, transaction);
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Title:
        <input type="text" value={title} onChange={e => setTitle(e.target.value)} />
      </label>
      <label>
        Description:
        <textarea value={description} onChange={e => setDescription(e.target.value)} />
      </label>
      {/* Fields for other transaction properties */}
      <button type="submit">Update Transaction</button>
    </form>
  );
};

export default UpdateTransaction;
