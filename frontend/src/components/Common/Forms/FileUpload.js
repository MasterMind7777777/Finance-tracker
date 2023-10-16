import { useState } from 'react';
import { ActionElementType } from '../constants/actionElementType';
import PropTypes from 'prop-types';
import { logMessage } from '../../../api/loging';

const FileInputComponent = ({ refreshFile, children }) => {
  const [status, setStatus] = useState('IDLE');
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  const onFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setStatus('SELECTED');
      setError(null);
      setFile(selectedFile);
      refreshFile(selectedFile);
      logMessage('info', 'File selected successfully', 'FileInputComponent'); // Log success
    } else {
      setError('No file selected');
      setStatus('FAILED');
      logMessage('error', 'No file was selected', 'FileInputComponent'); // Log failure
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
