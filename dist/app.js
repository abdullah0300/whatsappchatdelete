document.querySelectorAll('a[download]').forEach(link => {
  link.addEventListener('click', () => {
    const message = document.querySelector('#download-message');
    message.textContent = 'After downloading, extract the ZIP and open ChatSelect.exe. Start with 100 messages for your first run.';
  });
});
