import React, { useState, useEffect } from 'react';
import { getTransactionList, updateTransaction } from '../../api/transaction';
import PropTypes from 'prop-types';
import { logMessage } from '../../api/loging';

const UpdateTransaction = ({ match }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  // Add states for other transaction fields

  useEffect(() => {
    logMessage(
      'info',
      'UpdateTransaction component mounted.',
      'UpdateTransaction',
    );
    const getTransaction = async () => {
      try {
        logMessage(
          'info',
          'Fetching transaction details.',
          'UpdateTransaction',
        );
        const transaction = await getTransactionList(match.params.id);
        setTitle(transaction.title);
        setDescription(transaction.description);
        // Set other fields...
        logMessage(
          'info',
          `Transaction details fetched: ${JSON.stringify(transaction)}`,
          'UpdateTransaction',
        );
      } catch (error) {
        logMessage(
          'error',
          `Failed to fetch transaction: ${error.message}`,
          'UpdateTransaction',
        );
      }
    };

    getTransaction();
  }, [match.params.id]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const transaction = {
      title,
      description,
      // Other fields...
    };

    try {
      logMessage(
        'info',
        `Updating transaction with id ${match.params.id}.`,
        'UpdateTransaction',
      );
      await updateTransaction(match.params.id, transaction);
      logMessage(
        'info',
        `Successfully updated transaction with id ${match.params.id}.`,
        'UpdateTransaction',
      );
    } catch (error) {
      logMessage(
        'error',
        `Failed to update transaction: ${error.message}`,
        'UpdateTransaction',
      );
    }
  };

  // Add PropTypes validation for the 'match' prop
  UpdateTransaction.propTypes = {
    match: PropTypes.shape({
      params: PropTypes.shape({
        id: PropTypes.string.isRequired,
      }).isRequired,
    }).isRequired,
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Title:
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </label>
      <label>
        Description:
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </label>
      {/* Fields for other transaction properties */}
      <button type="submit">Update Transaction</button>
    </form>
  );
};

export default UpdateTransaction;
