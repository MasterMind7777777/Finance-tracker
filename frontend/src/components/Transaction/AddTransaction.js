import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import the useNavigate hook
import { createTransaction } from '../../api/transaction';

const AddTransaction = () => {
  const navigate = useNavigate(); // Get the navigate function
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState(0); // Default value of 0 for amount, change it as needed
  // Add states for other transaction fields

  const handleSubmit = async event => {
    event.preventDefault();

    const transaction = {
      title,
      description,
      amount, // Include the amount field in the transaction object
      // Other fields...
    };

    // Assuming createTransaction returns the newly created transaction with an ID
    const newTransaction = await createTransaction(transaction);

    setTitle('');
    setDescription('');
    setAmount(0); // Reset the amount field after form submission
    // Clear other fields...

    // Navigate to the detail page of the newly created transaction
    navigate(`/transactions/${newTransaction.id}`); // Replace 'id' with the actual property containing the ID
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
      <label>
        Amount:
        <input type="number" value={amount} onChange={e => setAmount(e.target.value)} />
      </label>
      {/* Fields for other transaction properties */}
      <button type="submit">Add Transaction</button>
    </form>
  );
};

export default AddTransaction;
