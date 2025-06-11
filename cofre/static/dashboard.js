document.addEventListener("DOMContentLoaded", function () {
  // Campos de senha
  const passInput = document.getElementById("passValue");
  const titleInput = document.getElementById("passTitle");
  const toggleBtn = document.getElementById("togglePassword");
  const generateBtn = document.getElementById("generatePassword");
  const passwordForm = document.getElementById("passwordForm");
  const passwordList = document.getElementById("passwordList");

  // Campos de nota
  const noteForm = document.getElementById("noteForm");
  const noteTitle = document.getElementById("noteTitle");
  const noteContent = document.getElementById("noteContent");
  const noteList = document.getElementById("noteList");

  // Arrays para armazenar dados localmente (temporário)
  let passwords = JSON.parse(localStorage.getItem("passwords") || "[]");
  let notes = JSON.parse(localStorage.getItem("notes") || "[]");

  // Alternar visibilidade da senha
  if (toggleBtn && passInput) {
    toggleBtn.addEventListener("click", () => {
      const isHidden = passInput.type === "password";
      passInput.type = isHidden ? "text" : "password";
      toggleBtn.textContent = isHidden ? "🙈" : "👁️";
    });
  }

  // Gerar senha aleatória
  if (generateBtn && passInput) {
    generateBtn.addEventListener("click", () => {
      passInput.value = generateSecurePassword(12);
    });
  }

  function generateSecurePassword(length = 12) {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*";
    return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
  }

  // Salvar senha
  if (passwordForm) {
    passwordForm.addEventListener("submit", function (e) {
      e.preventDefault();
      
      const title = titleInput.value.trim();
      const password = passInput.value.trim();
      
      if (!title || !password) {
        alert("Por favor, preencha todos os campos.");
        return;
      }

      const newPassword = {
        id: Date.now(),
        title: title,
        password: password,
        date: new Date().toLocaleDateString()
      };

      passwords.push(newPassword);
      localStorage.setItem("passwords", JSON.stringify(passwords));
      
      // Limpar formulário
      titleInput.value = "";
      passInput.value = "";
      
      // Atualizar lista
      displayPasswords();
      
      alert("Senha salva com sucesso!");
    });
  }

  // Salvar nota
  if (noteForm) {
    noteForm.addEventListener("submit", function (e) {
      e.preventDefault();
      
      const title = noteTitle.value.trim();
      const content = noteContent.value.trim();
      
      if (!title || !content) {
        alert("Por favor, preencha todos os campos.");
        return;
      }

      const newNote = {
        id: Date.now(),
        title: title,
        content: content,
        date: new Date().toLocaleDateString()
      };

      notes.push(newNote);
      localStorage.setItem("notes", JSON.stringify(notes));
      
      // Limpar formulário
      noteTitle.value = "";
      noteContent.value = "";
      
      // Atualizar lista
      displayNotes();
      
      alert("Nota salva com sucesso!");
    });
  }

  // Exibir senhas
  function displayPasswords() {
    if (!passwordList) return;
    
    if (passwords.length === 0) {
      passwordList.innerHTML = "<p style='text-align: center; color: #666;'>Nenhuma senha salva ainda.</p>";
      return;
    }

    passwordList.innerHTML = passwords.map(item => `
      <div class="item">
        <h3>🔑 ${item.title}</h3>
        <p><strong>Senha:</strong> <span style="font-family: monospace;">••••••••</span> 
           <button onclick="togglePasswordVisibility(${item.id})" class="btn-info">👁️ Ver</button>
        </p>
        <p><small>📅 Salvo em: ${item.date}</small></p>
        <button onclick="deletePassword(${item.id})" class="btn-danger">🗑️ Excluir</button>
      </div>
    `).join('');
  }

  // Exibir notas
  function displayNotes() {
    if (!noteList) return;
    
    if (notes.length === 0) {
      noteList.innerHTML = "<p style='text-align: center; color: #666;'>Nenhuma nota salva ainda.</p>";
      return;
    }

    noteList.innerHTML = notes.map(item => `
      <div class="item">
        <h3>📝 ${item.title}</h3>
        <p style="white-space: pre-wrap;">${item.content}</p>
        <p><small>📅 Salvo em: ${item.date}</small></p>
        <button onclick="deleteNote(${item.id})" class="btn-danger">🗑️ Excluir</button>
      </div>
    `).join('');
  }

  // Funções globais para os botões
  window.togglePasswordVisibility = function(id) {
    const password = passwords.find(p => p.id === id);
    if (password) {
      alert(`🔑 Senha para ${password.title}:\n\n${password.password}`);
    }
  };

  window.deletePassword = function(id) {
    if (confirm("🗑️ Tem certeza que deseja excluir esta senha?")) {
      passwords = passwords.filter(p => p.id !== id);
      localStorage.setItem("passwords", JSON.stringify(passwords));
      displayPasswords();
    }
  };

  window.deleteNote = function(id) {
    if (confirm("🗑️ Tem certeza que deseja excluir esta nota?")) {
      notes = notes.filter(n => n.id !== id);
      localStorage.setItem("notes", JSON.stringify(notes));
      displayNotes();
    }
  };

  // Carregar dados ao iniciar
  displayPasswords();
  displayNotes();
});