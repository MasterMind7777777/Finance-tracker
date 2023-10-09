import { useState } from 'react';
import { ActionElementType } from '../constants/actionElementType';
import PropTypes from 'prop-types';

const FileInputComponent = ({ children }) => {
  const [status, setStatus] = useState('IDLE');
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setStatus('SELECTED');
      setError(null);
      setFile(selectedFile);
    } else {
      setError('No file selected');
      setStatus('FAILED');
    }
  };

  const elements = [
    {
      type: ActionElementType.FILE,
      props: {
        type: 'file',
        onChange: onFileChange,
        id: 'file-input',
        file,
      },
    },
    {
      type: ActionElementType.STATUS,
      props: { status },
    },
    {
      type: ActionElementType.ERROR,
      props: { error },
    },
  ];

  return children(elements);
};

FileInputComponent.propTypes = {
  children: PropTypes.func.isRequired,
};

export default FileInputComponent;
