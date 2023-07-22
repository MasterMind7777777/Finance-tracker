import React from 'react';
import WithFormVisibility from './WithFormVisibility';

const ListWithAdd = (ListComponent, AddComponent, useFormVisibility = true) => {
  const AddComponentWithOptionalVisibility = useFormVisibility ? WithFormVisibility(AddComponent) : AddComponent;

  return () => (
    <div>
      <AddComponentWithOptionalVisibility />
      <ListComponent />
    </div>
  );
};

export default ListWithAdd;
