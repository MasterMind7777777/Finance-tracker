function showChildTransactions(transactionId) {
  // Get the parent transaction element
  const parentTransactionElement = document.getElementById(`transaction-${transactionId}`);

  // Get the child transactions container element
  const childTransactionsContainer = parentTransactionElement.querySelector('.child-transactions-container');
  
  childTransactionsContainer.classList.toggle('show');
}