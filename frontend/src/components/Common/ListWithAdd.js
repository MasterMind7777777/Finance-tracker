import React, { useEffect } from 'react'; // Import useEffect
import WithFormVisibility from './WithFormVisibility';
import { logMessage } from '../../api/loging'; // Importing logMessage function

const ListWithAdd = (ListComponent, AddComponent, useFormVisibility = true) => {
  const AddComponentWithOptionalVisibility = useFormVisibility
    ? WithFormVisibility(AddComponent)
    : AddComponent;

  const EnhancedComponent = () => {
    // Log when the component mounts and unmounts
    useEffect(() => {
      logMessage('info', 'ListWithAdd component mounted', 'ListWithAdd');

      return () => {
        logMessage('info', 'ListWithAdd component unmounted', 'ListWithAdd');
      };
    }, []);

    return (
      <div>
        <AddComponentWithOptionalVisibility />
        <ListComponent />
      </div>
    );
  };

  EnhancedComponent.displayName = `ListWithAdd(${getDisplayName(
    ListComponent,
  )}, ${getDisplayName(AddComponent)})`;

  return EnhancedComponent;
};

function getDisplayName(WrappedComponent) {
  return WrappedComponent.displayName || WrappedComponent.name || 'Component';
}

export default ListWithAdd;
