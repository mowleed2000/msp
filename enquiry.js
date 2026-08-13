(function () {
    'use strict';

    function handleEnquiry(event) {
        event.preventDefault();

        var form = event.target;
        var feedback = document.getElementById('formFeedback');
        var submitBtn = form.querySelector('button[type="submit"]');
        var originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';
        }

        var nameEl = document.getElementById('name');
        var phoneEl = document.getElementById('phone');
        var deviceEl = document.getElementById('device');
        var issueEl = document.getElementById('issue');
        var conditionEl = document.getElementById('condition');

        var formData = new FormData();
        formData.append('access_key', '5bc83c79-247a-42c2-901d-72ec0b4e0573');
        formData.append('name', nameEl ? nameEl.value : '');
        formData.append('phone', phoneEl ? phoneEl.value : '');

        if (deviceEl && conditionEl) {
            formData.append('subject', 'Trade-In Valuation: ' + deviceEl.value);
            formData.append('details', 'Device: ' + deviceEl.value + '\nCondition: ' + conditionEl.value);
        } else if (deviceEl && issueEl) {
            formData.append('subject', 'New Repair Enquiry: ' + deviceEl.value);
            formData.append('details', 'Device: ' + deviceEl.value + '\nIssue: ' + issueEl.value);
        } else {
            formData.append('subject', 'Website Enquiry');
        }

        fetch('https://api.web3forms.com/submit', {
            method: 'POST',
            body: formData
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (!feedback) return;
                if (data.success) {
                    feedback.style.color = '#10b981';
                    feedback.textContent = 'Enquiry sent! We will contact you shortly.';
                    form.reset();
                } else {
                    feedback.style.color = '#ef4444';
                    feedback.textContent = 'Submission failed, please try again.';
                }
            })
            .catch(function () {
                if (feedback) {
                    feedback.style.color = '#ef4444';
                    feedback.textContent = 'Submission failed, check your network connection.';
                }
            })
            .finally(function () {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnHtml;
                }
            });
    }

    window.handleEnquiry = handleEnquiry;
})();
