document.addEventListener("DOMContentLoaded", function () {
  // Remove toda a lógica de localStorage
  // O Django vai cuidar da autenticação
  console.log("Login page page");
    
  const loginForm = document.getElementById("loginForm");
    
  if (loginForm) {
      loginForm.addEventListener("submit", function (e) {
          const username = document.querySelector('input[name="username"]').value.trim();
          const password = document.querySelector('input[name="password"]').value.trim();
            
          if (!username || !password) {
              e.preventDefault();
              alert("Por favor, preencha todos os campos.");
              return;
          }
      });
  }
});
