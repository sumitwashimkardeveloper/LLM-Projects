const API_BASE_URL = "http://localhost:8000/api";
let authToken = localStorage.getItem("authToken");
let currentUser = null;
let currentPromptId = null;
let authMode = "login";

if (authToken) {
    initializeApp();
} else {
    showAuthModal();
}

function showMessage(message, type = "success", elementId = "alert") {
    const alertEl = document.getElementById(elementId);
    alertEl.textContent = message;
    alertEl.className = `alert ${type}`;
    if (type === "success") {
        setTimeout(() => alertEl.classList.remove("success"), 3000);
    }
}

async function handleAuth(event) {
    event.preventDefault();
    const email = document.getElementById("authEmail").value;
    const password = document.getElementById("authPassword").value;
    const fullName = document.getElementById("authFullName").value;

    try {
        if (authMode === "login") {
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);

            const response = await fetch(`${API_BASE_URL}/auth/token`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Invalid credentials");
            }

            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem("authToken", authToken);
            closeAuthModal();
            initializeApp();
        } else {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    full_name: fullName,
                }),
            });

            if (!response.ok) {
                throw new Error("Registration failed");
            }

            showMessage("Registration successful! Logging in...", "success", "authAlert");
            authMode = "login";
            document.getElementById("authTitle").textContent = "Login";
            document.getElementById("fullNameGroup").style.display = "none";
            document.getElementById("authPassword").value = "";
            setTimeout(() => handleAuth(event), 1500);
        }
    } catch (error) {
        showMessage(error.message, "error", "authAlert");
    }
}

function toggleAuthMode() {
    authMode = authMode === "login" ? "register" : "login";
    document.getElementById("authTitle").textContent = authMode === "login" ? "Login" : "Register";
    document.getElementById("fullNameGroup").style.display = authMode === "register" ? "block" : "none";
    document.getElementById("authEmail").value = "";
    document.getElementById("authPassword").value = "";
    document.getElementById("authFullName").value = "";
}

function openAuthModal() {
    document.getElementById("authContainer").classList.add("active");
}

function closeAuthModal() {
    document.getElementById("authContainer").classList.remove("active");
}

function showAuthModal() {
    document.getElementById("mainContent").style.display = "none";
    document.getElementById("authBtn").style.display = "inline-block";
    document.getElementById("logoutBtn").style.display = "none";
    openAuthModal();
}

async function initializeApp() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (!response.ok) {
            throw new Error("Session expired");
        }

        currentUser = await response.json();
        document.getElementById("authBtn").style.display = "none";
        document.getElementById("logoutBtn").style.display = "inline-block";
        document.getElementById("userEmail").textContent = currentUser.email;
        document.getElementById("authContainer").classList.remove("active");
        document.getElementById("mainContent").style.display = "grid";
        loadPrompts();
    } catch (error) {
        logout();
    }
}

function logout() {
    localStorage.removeItem("authToken");
    authToken = null;
    currentUser = null;
    showAuthModal();
}

async function loadPrompts() {
    try {
        const response = await fetch(`${API_BASE_URL}/prompts/`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (!response.ok) throw new Error("Failed to load prompts");

        const data = await response.json();
        renderPrompts(data.prompts);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderPrompts(prompts) {
    const promptsList = document.getElementById("promptsList");

    if (prompts.length === 0) {
        promptsList.innerHTML =
            '<div class="empty-state"><h3>No prompts yet</h3><p>Create your first prompt to get started</p></div>';
        return;
    }

    promptsList.innerHTML = prompts
        .map(
            (prompt) => `
        <div class="prompt-card" onclick="viewPromptDetail(${prompt.id})">
            <h3>${prompt.title}</h3>
            <p>${prompt.description || "No description"}</p>
            <div class="prompt-meta">
                <span class="badge">${prompt.model}</span>
                <span class="badge">${prompt.versions.length} versions</span>
                <span>${new Date(prompt.created_at).toLocaleDateString()}</span>
            </div>
            <div class="prompt-actions" onclick="event.stopPropagation()">
                <button onclick="openCreateVersionModal(${prompt.id})">➕ New Version</button>
                <button class="secondary" onclick="editPrompt(${prompt.id})">✏️ Edit</button>
                <button class="danger" onclick="deletePrompt(${prompt.id})">🗑️ Delete</button>
            </div>
        </div>
    `
        )
        .join("");
}

async function viewPromptDetail(promptId) {
    try {
        const response = await fetch(`${API_BASE_URL}/prompts/${promptId}`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (!response.ok) throw new Error("Failed to load prompt");

        const prompt = await response.json();
        const detailDiv = document.getElementById("promptDetailContent");

        const versionsHtml = prompt.versions
            .map(
                (v) => `
            <div class="version-item">
                <strong>Version ${v.version_number}</strong>
                <p>${v.change_description || "No description"}</p>
                <small>${new Date(v.created_at).toLocaleString()}</small>
                <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; margin-top: 10px;">${v.content}</pre>
                ${v.version_number > 1 ? `<button onclick="rollbackVersion(${prompt.id}, ${v.id})" class="secondary">↩️ Rollback</button>` : ""}
            </div>
        `
            )
            .join("");

        detailDiv.innerHTML = `
            <button onclick="showSection('prompts')" class="secondary">← Back</button>
            <h3>${prompt.title}</h3>
            <p>${prompt.description}</p>
            <div class="prompt-meta">
                <span class="badge">${prompt.model}</span>
                <span>${new Date(prompt.created_at).toLocaleDateString()}</span>
            </div>
            <h4 style="margin-top: 20px;">Current Prompt</h4>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto;">${prompt.content}</pre>
            <h4 style="margin-top: 20px;">Version History</h4>
            ${versionsHtml}
        `;

        showSection("promptDetail");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function openCreateModal() {
    currentPromptId = null;
    document.getElementById("promptModalTitle").textContent = "Create Prompt";
    document.getElementById("promptTitle").value = "";
    document.getElementById("promptDescription").value = "";
    document.getElementById("promptContent").value = "";
    document.getElementById("promptModel").value = "gpt-3.5-turbo";
    document.getElementById("promptTags").value = "";
    document.getElementById("promptModal").classList.add("active");
}

function editPrompt(promptId) {
    currentPromptId = promptId;
    // TODO: Load prompt details and populate form
    openCreateModal();
}

function closePromptModal() {
    document.getElementById("promptModal").classList.remove("active");
    currentPromptId = null;
}

async function handleSavePrompt(event) {
    event.preventDefault();

    const promptData = {
        title: document.getElementById("promptTitle").value,
        description: document.getElementById("promptDescription").value,
        content: document.getElementById("promptContent").value,
        model: document.getElementById("promptModel").value,
        tags: document.getElementById("promptTags").value.split(",").map((t) => t.trim()),
    };

    try {
        const method = currentPromptId ? "PUT" : "POST";
        const url = currentPromptId ? `${API_BASE_URL}/prompts/${currentPromptId}` : `${API_BASE_URL}/prompts/`;

        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify(promptData),
        });

        if (!response.ok) throw new Error("Failed to save prompt");

        showMessage(currentPromptId ? "Prompt updated!" : "Prompt created!", "success");
        closePromptModal();
        loadPrompts();
    } catch (error) {
        showMessage(error.message, "error", "promptAlert");
    }
}

async function deletePrompt(promptId) {
    if (!confirm("Are you sure you want to delete this prompt?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/prompts/${promptId}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (!response.ok) throw new Error("Failed to delete prompt");

        showMessage("Prompt deleted!", "success");
        loadPrompts();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function openCreateVersionModal(promptId) {
    currentPromptId = promptId;
    document.getElementById("versionContent").value = "";
    document.getElementById("versionDescription").value = "";
    document.getElementById("versionModal").classList.add("active");
}

function closeVersionModal() {
    document.getElementById("versionModal").classList.remove("active");
    currentPromptId = null;
}

async function handleCreateVersion(event) {
    event.preventDefault();

    const versionData = {
        content: document.getElementById("versionContent").value,
        model: document.getElementById("versionModel").value,
        change_description: document.getElementById("versionDescription").value,
    };

    try {
        const response = await fetch(`${API_BASE_URL}/prompts/${currentPromptId}/versions`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify(versionData),
        });

        if (!response.ok) throw new Error("Failed to create version");

        showMessage("Version created!", "success");
        closeVersionModal();
        loadPrompts();
    } catch (error) {
        showMessage(error.message, "error", "versionAlert");
    }
}

async function rollbackVersion(promptId, versionId) {
    if (!confirm("Are you sure you want to rollback to this version?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/prompts/${promptId}/rollback/${versionId}`, {
            method: "POST",
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (!response.ok) throw new Error("Failed to rollback");

        showMessage("Rolled back to previous version!", "success");
        loadPrompts();
        viewPromptDetail(promptId);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function showSection(sectionId) {
    document.querySelectorAll(".section").forEach((s) => s.classList.remove("active"));
    document.getElementById(sectionId).classList.add("active");

    document.querySelectorAll(".nav-link").forEach((link) => link.classList.remove("active"));
    event.target.classList.add("active");
}
