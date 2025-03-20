function openForm(companyName) {
    document.getElementById('company-name').innerText = companyName;
    document.getElementById('overlay').style.display = 'flex';
}

function closeForm() {
    document.getElementById('overlay').style.display = 'none';
}

document.getElementById('enrollment-form').addEventListener('submit', function(event) {
    event.preventDefault();
    alert('Enrollment submitted!');
    closeForm();
});