import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTransaction } from '../../api/transaction';
import { getCategoryList } from '../../api/category'; // Import getCategoryList
import FormComponent from '../Common/forms/FormComponent.js';

const AddTransaction = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState(0);
  const [category, setCategory] = useState(''); // State for category
  const [categoryOptions, setCategoryOptions] = useState([]); // State to store category options

  // Fetch category options when the component mounts
  useEffect(() => {
    async function fetchCategories() {
      try {
        const response = await getCategoryList();
        if (Array.isArray(response)) {
          // Check if response.data is an array
          setCategoryOptions(response);
        } else {
          console.error('Response data is not an array'); // Debug log
        }
      } catch (error) {
        console.error('Error fetching categories: ', error);
      }
    }

    fetchCategories();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const transaction = {
      title,
      description,
      amount,
      category, // Include the selected category in the transaction object
    };

    const newTransaction = await createTransaction(transaction);

    setTitle('');
    setDescription('');
    setAmount(0);
    setCategory(''); // Reset the category field after form submission

    navigate(`/transactions/${newTransaction.id}`);
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
            placeholder: 'Title',
            value: title,
            onChange: (e) => setTitle(e.target.value),
            required: true,
          },
        },
        {
          label: 'Description',
          type: 'textarea',
          props: {
            placeholder: 'Description',
            value: description,
            onChange: (e) => setDescription(e.target.value),
          },
        },
        {
          label: 'Amount',
          type: 'number',
          props: {
            placeholder: 'Amount',
            value: amount,
            onChange: (e) => setAmount(e.target.value),
            required: true,
          },
        },
        {
          label: 'Category', // Add a field for the category dropdown
          type: 'select',
          props: {
            value: category,
            onChange: (e) => setCategory(e.target.value),
            required: true,
          },
          options: categoryOptions
            ? categoryOptions.map((categoryOption) => {
                return {
                  value: categoryOption.id,
                  label: categoryOption.name,
                };
              })
            : [], // Default to an empty array if categoryOptions is not available
        },
        // ... add more fields if needed
      ]}
    />
  );
};

export default AddTransaction;
