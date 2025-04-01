document.addEventListener("DOMContentLoaded", function () {
    function populateCities() {
        const state = document.getElementById("state").value;
        const cityDropdown = document.getElementById("city");
        cityDropdown.innerHTML = '<option>Select City</option>';
       
        const cities = {
            "Andhra Pradesh": ["Vijayawada"],
            "Tamil Nadu": ["Chennai"],
            "Haryana": ["Gurugram"],
            "West Bengal": ["Kolkata"],
            "Telangana": ["Hyderabad"],
            "Maharashtra": ["Mumbai"],
            "Karnataka": ["Bengaluru"]
        };
       
        if (state in cities) {
            cities[state].forEach(city => {
                let option = document.createElement("option");
                option.value = city;
                option.textContent = city;
                cityDropdown.appendChild(option);
            });
        }
    }

    document.getElementById("state").addEventListener("change", populateCities);

    document.getElementById('registrationForm').addEventListener('submit', function(event) {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (password !== confirmPassword) {
            event.preventDefault();
            alert('Passwords do not match!');
        }
    });
});
