import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTransaction } from '../../api/transaction';
import { getCategoryList } from '../../api/category';
import FormComponent from '../Common/Forms/FormBase';
import { logMessage } from '../../api/loging'; // Import logMessage function

const AddTransaction = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState(0);
  const [category, setCategory] = useState('');
  const [categoryOptions, setCategoryOptions] = useState([]);

  useEffect(() => {
    async function fetchCategories() {
      try {
        const response = await getCategoryList();
        if (Array.isArray(response)) {
          setCategoryOptions(response);
          logMessage(
            'info',
            'Successfully fetched category list',
            'AddTransaction',
          );
        } else {
          logMessage('warn', 'Response data is not an array', 'AddTransaction');
        }
      } catch (error) {
        logMessage(
          'error',
          `Error fetching categories: ${error.message}`,
          'AddTransaction',
        );
      }
    }

    fetchCategories();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const transaction = {
        title,
        description,
        amount,
        category,
      };

      const newTransaction = await createTransaction(transaction);

      setTitle('');
      setDescription('');
      setAmount(0);
      setCategory('');

      navigate(`/transactions/${newTransaction.id}`);
      logMessage('info', 'Transaction successfully added', 'AddTransaction');
    } catch (error) {
      logMessage(
        'error',
        `Failed to add transaction: ${error.message}`,
        'AddTransaction',
      );
    }
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
