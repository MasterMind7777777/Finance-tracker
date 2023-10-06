import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { splitTransaction } from '../../api/transaction';

const SplitTransactionForm = () => {
  const { id: transactionId } = useParams();
  const [splits, setSplits] = useState([{ user: '', amount: '' }]);

  const handleSplitChange = (index, field, value) => {
    const newSplits = [...splits];
    newSplits[index][field] = value;
    setSplits(newSplits);
  };

  const handleAddSplit = () => {
    setSplits([...splits, { user: '', amount: '' }]);
  };

  const handleRemoveSplit = (index) => {
    const newSplits = [...splits];
    newSplits.splice(index, 1);
    setSplits(newSplits);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await splitTransaction(transactionId, { splits });
    // TODO: Handle the response
    console.log(response);
  };

  return (
    <form onSubmit={handleSubmit}>
      {splits.map((split, index) => (
        <div key={index}>
          <input
            type="number"
            value={split.user}
            onChange={(e) => handleSplitChange(index, 'user', e.target.value)}
            placeholder="User ID"
            required
          />
          <input
            type="number"
            value={split.amount}
            onChange={(e) => handleSplitChange(index, 'amount', e.target.value)}
            placeholder="Amount"
            required
          />
          <button type="button" onClick={() => handleRemoveSplit(index)}>
            Remove
          </button>
        </div>
      ))}
      <button type="button" onClick={handleAddSplit}>
        Add Split
      </button>
      <button type="submit">Split Transaction</button>
    </form>
  );
};

export default SplitTransactionForm;
