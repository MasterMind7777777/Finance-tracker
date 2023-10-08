import React, { useEffect, useState } from 'react';
import { getCategoryList } from '../../api/category';
import ListRenderer from '../Common/lists/listBase';

const CategoryList = () => {
  const [categories, setCategories] = useState([]);
  const [itemTitles, setItemTitles] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await getCategoryList();
        setCategories(response);

        // Create titles for each category, this could be anything based on your needs
        const titles = response.map((category) => `Category: ${category.name}`);
        setItemTitles(titles); // Set the titles
      } catch (error) {
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
        itemTitles={itemTitles} // Pass the titles to ListRenderer
        contentConfig={contentConfig}
      />
    </div>
  );
};

export default CategoryList;
