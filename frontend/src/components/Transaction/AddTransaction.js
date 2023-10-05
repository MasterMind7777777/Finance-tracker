import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import the useNavigate hook
import { createTransaction } from '../../api/transaction';
import '../../styles/forms/forms_main.css';
import '../../styles/forms/add_transaction.css';
import FormComponent from '../Common/forms/FormComponent.js';

const AddTransaction = () => {
  const navigate = useNavigate(); // Get the navigate function
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState(0); // Default value of 0 for amount, change it as needed
  // Add states for other transaction fields

  const handleSubmit = async (event) => {
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
    <FormComponent
      formClassName="add-transaction-form"
      buttonText="Add Transaction"
      onSubmit={handleSubmit}
      fields={[
        {
          label: 'Title',
          type: 'text',
          props: {
            value: title,
            onChange: (e) => setTitle(e.target.value),
          },
        },
        {
          label: 'Description',
          type: 'textarea',
          props: {
            value: description,
            onChange: (e) => setDescription(e.target.value),
          },
        },
        {
          label: 'Amount',
          type: 'number',
          props: {
            value: amount,
            onChange: (e) => setAmount(e.target.value),
          },
        },
        // ... add more fields if needed
      ]}
    />
  );
};

export default AddTransaction;
