import React from 'react';
import WithFormVisibility from './WithFormVisibility';

const ListWithAdd = (ListComponent, AddComponent, useFormVisibility = true) => {
  const AddComponentWithOptionalVisibility = useFormVisibility
    ? WithFormVisibility(AddComponent)
    : AddComponent;

  const EnhancedComponent = () => (
    <div>
      <AddComponentWithOptionalVisibility />
      <ListComponent />
    </div>
  );

  EnhancedComponent.displayName = `ListWithAdd(${getDisplayName(
    ListComponent,
  )}, ${getDisplayName(AddComponent)})`;

  return EnhancedComponent;
};

function getDisplayName(WrappedComponent) {
  return WrappedComponent.displayName || WrappedComponent.name || 'Component';
}

export default ListWithAdd;
