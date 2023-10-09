import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { splitTransaction } from '../../api/transaction';
import { ActionElementType } from '../Common/constants/actionElementType';
import PropTypes from 'prop-types';

const SplitTransactionForm = ({ children }) => {
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

  const splitInputs = splits.map((split, index) => ({
    type: ActionElementType.GROUP,
    props: { index, split },
    children: [
      {
        type: ActionElementType.INPUT,
        props: {
          type: 'number',
          value: split.user,
          onChange: (e) => handleSplitChange(index, 'user', e.target.value),
          placeholder: 'User ID',
          required: true,
        },
      },
      {
        type: ActionElementType.INPUT,
        props: {
          type: 'number',
          value: split.amount,
          onChange: (e) => handleSplitChange(index, 'amount', e.target.value),
          placeholder: 'Amount',
          required: true,
        },
      },
      {
        type: ActionElementType.BUTTON,
        props: {
          onClick: () => handleRemoveSplit(index),
          label: 'Remove',
        },
      },
    ],
  }));

  const elements = [
    {
      type: ActionElementType.SUBMIT,
      props: {
        onSubmit: handleSubmit,
      },
      children: [
        ...splitInputs,
        {
          type: ActionElementType.BUTTON,
          props: {
            onClick: handleAddSplit,
            label: 'Add Split',
          },
        },
        {
          type: ActionElementType.BUTTON,
          props: {
            type: 'submit',
            label: 'Split Transaction',
          },
        },
      ],
    },
  ];

  return children(elements);
};

SplitTransactionForm.propTypes = {
  children: PropTypes.func.isRequired,
};

export default SplitTransactionForm;
