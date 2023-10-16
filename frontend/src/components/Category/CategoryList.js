import React, { useEffect, useState } from 'react';
import { getCategoryList } from '../../api/category';
import ListRenderer from '../Common/Lists/ListBase';
import { logMessage } from '../../api/loging'; // Import centralized logging function

const CategoryList = () => {
  const [categories, setCategories] = useState([]);
  const [itemTitles, setItemTitles] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await getCategoryList();
        setCategories(response);

        const titles = response.map((category) => `Category: ${category.name}`);
        setItemTitles(titles);

        logMessage(
          'info',
          'Successfully fetched category list',
          'CategoryList',
        ); // Log the successful fetch
      } catch (error) {
        logMessage(
          'error',
          `Failed to fetch category list. Error: ${error.message}`,
          'CategoryList',
        ); // Log the error
        console.error(error);
      }
    };

    fetchCategories();
  }, []);

  const contentConfig = {
    title: 'Name',
    paragraphs: [
      {
        label: 'Type',
        key: 'type',
      },
    ],
    links: [
      {
        link: 'id',
        linkPrefix: '/categories/',
        linkText: 'View Details',
      },
    ],
  };

  return (
    <div>
      <h2>Category List</h2>
      <ListRenderer
        items={categories}
        keyExtractor={(item, index) => `${item.id}-${index}`}
        title="Categories"
        itemTitles={itemTitles}
        contentConfig={contentConfig}
      />
    </div>
  );
};

export default CategoryList;
