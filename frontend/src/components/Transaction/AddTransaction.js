import React, { useState } from 'react';
import { createTransaction } from '../../api/transaction';

const AddTransaction = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  // Add states for other transaction fields

  const handleSubmit = async event => {
    event.preventDefault();

    const transaction = {
      title,
      description,
      // Other fields...
    };

    await createTransaction(transaction);

    setTitle('');
    setDescription('');
    // Clear other fields...
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
      <button type="submit">Add Transaction</button>
    </form>
  );
};

export default AddTransaction;
