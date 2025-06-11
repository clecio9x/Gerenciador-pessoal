document.addEventListener("DOMContentLoaded", function () {
  // Remove toda a lógica de localStorage
  // O Django vai cuidar do registro via POST
  console.log("Register page loaded");
    
  // Se você quiser adicionar alguma validação no frontend, pode fazer aqui
  const registerForm = document.getElementById("registerForm");
    
  if (registerForm) {
      registerForm.addEventListener("submit", function (e) {
          const username = document.querySelector('input[name="username"]').value.trim();
          const password = document.querySelector('input[name="password"]').value.trim();
            
          if (!username || !password) {
              e.preventDefault();
              alert("Por favor, preencha todos os campos.");
              return;
          }
            
          if (password.length < 4) {
              e.preventDefault();
              alert("A senha deve ter pelo menos 4 caracteres.");
              return;
          }
      });
  }
});
