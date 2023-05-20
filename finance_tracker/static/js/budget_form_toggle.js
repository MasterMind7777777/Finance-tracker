document.getElementById('toggle-form-btn').addEventListener('click', function() {
    var formWrapper = document.getElementById('budget-form-wrapper');
    var btnText = this.innerHTML;
    if (formWrapper.style.display === 'none') {
        formWrapper.style.display = 'block';
        this.innerHTML = 'Hide Budget Limit Form';
    } else {
        formWrapper.style.display = 'none';
        this.innerHTML = 'Add Budget Limit';
    }
});