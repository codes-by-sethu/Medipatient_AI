// MediPatient AI - Complete JavaScript
// Version 4.1 - Fixed PDF Export & Navigation

class MediPatientAI {
    constructor() {
        this.init();
    }

    init() {
        // DOM Elements
        this.setupDOM();
        
        // Initialize components
        this.setupEventListeners();
        this.setupTestCases();
        this.setupSymptoms();
        this.initializeCharts();
        this.setupParticles();
        
        // Simulate API connection
        this.simulateAPIStatus();
        
        console.log('MediPatient AI initialized successfully');
    }

    setupDOM() {
        // Get all necessary DOM elements
        this.elements = {
            // Forms and inputs
            clinicalForm: document.getElementById('clinicalForm'),
            ageSlider: document.getElementById('ageSlider'),
            ageInput: document.getElementById('age'),
            ageValue: document.getElementById('ageValue'),
            ageCategory: document.getElementById('ageCategory'),
            painSlider: document.getElementById('painSlider'),
            painValue: document.getElementById('painValue'),
            painDescription: document.getElementById('painDescription'),
            
            // Vital signs
            tempSlider: document.getElementById('tempSlider'),
            tempValue: document.getElementById('tempValue'),
            hrSlider: document.getElementById('hrSlider'),
            hrValue: document.getElementById('hrValue'),
            sbpSlider: document.getElementById('sbpSlider'),
            dbpSlider: document.getElementById('dbpSlider'),
            systolicBP: document.getElementById('systolicBP'),
            diastolicBP: document.getElementById('diastolicBP'),
            o2Slider: document.getElementById('o2Slider'),
            o2Value: document.getElementById('o2Value'),
            rrSlider: document.getElementById('rrSlider'),
            rrValue: document.getElementById('rrValue'),
            
            // Analysis
            analyzeBtn: document.getElementById('analyzeBtn'),
            loader: document.getElementById('loader'),
            dataPoints: document.getElementById('dataPoints'),
            aiConfidence: document.getElementById('aiConfidence'),
            
            // Results sections
            initialState: document.getElementById('initialState'),
            loadingState: document.getElementById('loadingState'),
            errorState: document.getElementById('errorState'),
            analysisProgress: document.getElementById('analysisProgress'),
            
            // Reports
            diagnosisReport: document.getElementById('diagnosisReport'),
            clinicalReport: document.getElementById('clinicalReport'),
            treatmentReport: document.getElementById('treatmentReport'),
            patientReport: document.getElementById('patientReport'),
            riskReport: document.getElementById('riskReport'),
            
            // System status
            genAiStatus: document.getElementById('genAiStatus'),
            genAiLoad: document.getElementById('genAiLoad'),
            genAiLoadValue: document.getElementById('genAiLoadValue'),
            apiStatus: document.getElementById('apiStatus'),
            
            // UI Components
            tabBtns: document.querySelectorAll('.tab-btn'),
            tabContents: document.querySelectorAll('.tab-content'),
            reportTabs: document.querySelectorAll('.report-tab'),
            reportSections: document.querySelectorAll('.report-section'),
            
            // Buttons and toggles
            clearForm: document.getElementById('clearForm'),
            showTestCases: document.getElementById('showTestCases'),
            testCasesPanel: document.getElementById('testCasesPanel'),
            closePanel: document.getElementById('closePanel'),
            retryBtn: document.getElementById('retryBtn'),
            notificationsBtn: document.getElementById('notificationsBtn'),
            notificationsDropdown: document.getElementById('notificationsDropdown'),
            voiceSearch: document.getElementById('voiceSearch'),
            voiceInput: document.getElementById('voiceInput'),
            selectAllBtn: document.getElementById('selectAllBtn'),
            customSymptom: document.getElementById('customSymptom'),
            addSymptom: document.getElementById('addSymptom'),
            selectedSymptomsCount: document.getElementById('selectedSymptomsCount'),

            // Export Buttons (ADDED)
            exportReportBtn: document.getElementById('exportReport'),
            printReportBtn: document.getElementById('printReport'),
            
            // AI Assistant
            aiAssistant: document.getElementById('aiAssistant'),
            assistantToggle: document.getElementById('assistantToggle'),
            assistantBody: document.getElementById('assistantBody'),
            aiQuery: document.getElementById('aiQuery'),
            sendQuery: document.getElementById('sendQuery'),
            
            // Charts
            aiModelChart: document.getElementById('aiModelChart'),
            bpChart: document.getElementById('bpChart').querySelector('canvas')
        };
    }

    setupEventListeners() {
        // Tab navigation
        this.elements.tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target));
        });

        // Report tab navigation
        this.elements.reportTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.switchReportTab(e.target));
        });

        // Age slider
        this.elements.ageSlider.addEventListener('input', (e) => {
            const value = e.target.value;
            this.elements.ageInput.value = value;
            this.elements.ageValue.textContent = `${value} years`;
            this.updateAgeCategory(value);
        });

        this.elements.ageInput.addEventListener('input', (e) => {
            const value = Math.min(120, Math.max(0, parseInt(e.target.value) || 0));
            this.elements.ageSlider.value = value;
            this.elements.ageValue.textContent = `${value} years`;
            this.updateAgeCategory(value);
        });

        // Pain slider
        this.elements.painSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.updatePainAssessment(value);
        });

        // Vital signs sliders
        this.setupVitalSliders();

        // Blood pressure sync
        this.elements.systolicBP.addEventListener('input', (e) => {
            const value = Math.min(250, Math.max(70, parseInt(e.target.value) || 120));
            this.elements.sbpSlider.value = value;
            this.updateBPStatus();
        });

        this.elements.diastolicBP.addEventListener('input', (e) => {
            const value = Math.min(150, Math.max(40, parseInt(e.target.value) || 80));
            this.elements.dbpSlider.value = value;
            this.updateBPStatus();
        });

        // Analyze button
        this.elements.analyzeBtn.addEventListener('click', () => this.analyzeClinicalData());

        // Clear form
        this.elements.clearForm.addEventListener('click', () => this.clearForm());

        // Test cases
        this.elements.showTestCases.addEventListener('click', () => {
            this.elements.testCasesPanel.classList.add('active');
        });

        this.elements.closePanel.addEventListener('click', () => {
            this.elements.testCasesPanel.classList.remove('active');
        });

        // Retry analysis
        this.elements.retryBtn.addEventListener('click', () => {
            this.hideError();
            this.analyzeClinicalData();
        });

        // Notifications
        this.elements.notificationsBtn.addEventListener('click', () => {
            this.elements.notificationsDropdown.classList.toggle('show');
        });

        // Voice search
        this.elements.voiceSearch.addEventListener('click', () => this.toggleVoiceSearch());
        this.elements.voiceInput.addEventListener('click', () => this.toggleVoiceInput());

        // Symptoms
        this.elements.selectAllBtn.addEventListener('click', () => this.selectCommonSymptoms());
        this.elements.addSymptom.addEventListener('click', () => this.addCustomSymptom());

        // Export Actions (FIXED)
        if (this.elements.exportReportBtn) {
            this.elements.exportReportBtn.addEventListener('click', () => this.exportNotes());
        }
        if (this.elements.printReportBtn) {
            this.elements.printReportBtn.addEventListener('click', () => this.printTreatmentPlan());
        }

        // AI Assistant
        this.elements.assistantToggle.addEventListener('click', () => {
            this.elements.aiAssistant.classList.toggle('collapsed');
        });

        this.elements.sendQuery.addEventListener('click', () => this.sendAIQuery());

        // Close notifications when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.notifications-wrapper')) {
                this.elements.notificationsDropdown.classList.remove('show');
            }
        });

        // Close test cases panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.test-cases-panel') && 
                !e.target.closest('#showTestCases') &&
                !e.target.closest('.load-case-btn')) {
                this.elements.testCasesPanel.classList.remove('active');
            }
        });
    }

    setupVitalSliders() {
        // Temperature
        this.elements.tempSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.elements.tempValue.textContent = `${value.toFixed(1)}°C`;
            this.updateVitalStatus('temp', value);
        });

        // Heart rate
        this.elements.hrSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.hrValue.textContent = `${value} bpm`;
            this.updateVitalStatus('hr', value);
        });

        // Blood pressure sliders
        this.elements.sbpSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.systolicBP.value = value;
            this.updateBPStatus();
        });

        this.elements.dbpSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.diastolicBP.value = value;
            this.updateBPStatus();
        });

        // Oxygen saturation
        this.elements.o2Slider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.o2Value.textContent = `${value}%`;
            this.updateVitalStatus('o2', value);
        });

        // Respiratory rate
        this.elements.rrSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.rrValue.textContent = `${value}/min`;
            this.updateVitalStatus('rr', value);
        });
    }

    setupTestCases() {
        const testCases = [
            {
                id: 'pneumonia',
                title: 'Community-Acquired Pneumonia',
                description: 'Fever, productive cough, dyspnea, crackles',
                icon: 'fas fa-lungs-virus',
                data: {
                    age: 65,
                    gender: 'male',
                    temperature: 38.5,
                    heartRate: 105,
                    systolicBP: 130,
                    diastolicBP: 85,
                    oxygen: 92,
                    respiratoryRate: 24,
                    painLevel: 7,
                    symptoms: ['fever', 'cough', 'shortness_of_breath', 'fatigue']
                }
            },
            {
                id: 'mi',
                title: 'Acute Myocardial Infarction',
                description: 'Chest pain, diaphoresis, nausea, ST elevation',
                icon: 'fas fa-heart-crack',
                data: {
                    age: 58,
                    gender: 'male',
                    temperature: 37.2,
                    heartRate: 95,
                    systolicBP: 150,
                    diastolicBP: 95,
                    oxygen: 96,
                    respiratoryRate: 20,
                    painLevel: 9,
                    symptoms: ['chest_pain', 'nausea', 'dizziness', 'fatigue']
                }
            },
            {
                id: 'uti',
                title: 'Urinary Tract Infection',
                description: 'Dysuria, frequency, suprapubic pain, fever',
                icon: 'fas fa-bacteria',
                data: {
                    age: 32,
                    gender: 'female',
                    temperature: 38.2,
                    heartRate: 88,
                    systolicBP: 118,
                    diastolicBP: 78,
                    oxygen: 98,
                    respiratoryRate: 18,
                    painLevel: 5,
                    symptoms: ['fever', 'fatigue']
                }
            },
            {
                id: 'normal',
                title: 'Normal Checkup',
                description: 'All vitals within normal limits',
                icon: 'fas fa-user-check',
                data: {
                    age: 45,
                    gender: 'female',
                    temperature: 37.0,
                    heartRate: 75,
                    systolicBP: 120,
                    diastolicBP: 80,
                    oxygen: 98,
                    respiratoryRate: 16,
                    painLevel: 2,
                    symptoms: []
                }
            }
        ];

        const grid = document.querySelector('.test-cases-grid');
        grid.innerHTML = '';

        testCases.forEach(testCase => {
            const card = document.createElement('div');
            card.className = 'test-case-card';
            card.dataset.case = testCase.id;
            
            card.innerHTML = `
                <div class="case-icon">
                    <i class="${testCase.icon}"></i>
                </div>
                <h4>${testCase.title}</h4>
                <p>${testCase.description}</p>
                <button class="load-case-btn">Load Scenario</button>
            `;

            card.querySelector('.load-case-btn').addEventListener('click', () => {
                this.loadTestCase(testCase);
                this.elements.testCasesPanel.classList.remove('active');
                this.showToast('Scenario loaded successfully', 'success');
            });

            grid.appendChild(card);
        });
    }

    setupSymptoms() {
        const symptoms = [
            { id: 'fever', label: 'Fever', icon: '🌡️' },
            { id: 'cough', label: 'Cough', icon: '🤧' },
            { id: 'shortness_of_breath', label: 'Shortness of Breath', icon: '😫' },
            { id: 'chest_pain', label: 'Chest Pain', icon: '💔' },
            { id: 'fatigue', label: 'Fatigue', icon: '😴' },
            { id: 'headache', label: 'Headache', icon: '🤕' },
            { id: 'nausea', label: 'Nausea', icon: '🤢' },
            { id: 'dizziness', label: 'Dizziness', icon: '💫' },
            { id: 'vomiting', label: 'Vomiting', icon: '🤮' },
            { id: 'diarrhea', label: 'Diarrhea', icon: '💩' },
            { id: 'rash', label: 'Rash', icon: '🔴' },
            { id: 'joint_pain', label: 'Joint Pain', icon: '🦵' }
        ];

        const grid = document.querySelector('.symptoms-grid');
        grid.innerHTML = '';

        symptoms.forEach(symptom => {
            const chip = document.createElement('label');
            chip.className = 'symptom-chip';
            
            chip.innerHTML = `
                <input type="checkbox" name="symptoms" value="${symptom.id}">
                <span class="chip-content">
                    <span class="chip-icon">${symptom.icon}</span>
                    <span class="chip-label">${symptom.label}</span>
                </span>
            `;

            chip.querySelector('input').addEventListener('change', () => {
                this.updateSymptomsCount();
            });

            grid.appendChild(chip);
        });

        this.updateSymptomsCount();
    }

    initializeCharts() {
        // Initialize AI Model Chart
        const ctx = this.elements.aiModelChart.getContext('2d');
        if (ctx) {
            this.aiModelChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array.from({length: 10}, (_, i) => i + 1),
                    datasets: [{
                        label: 'AI Confidence',
                        data: [92, 94, 93, 95, 96, 97, 96, 95, 96, 97],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { display: false },
                        y: { 
                            display: false,
                            min: 90,
                            max: 100
                        }
                    }
                }
            });
        }

        // Initialize BP Chart
        const bpCtx = this.elements.bpChart.getContext('2d');
        if (bpCtx) {
            this.bpChart = new Chart(bpCtx, {
                type: 'line',
                data: {
                    labels: ['', '', '', '', ''],
                    datasets: [
                        {
                            label: 'Systolic',
                            data: [110, 115, 120, 118, 122],
                            borderColor: '#ef4444',
                            borderWidth: 1,
                            tension: 0.4
                        },
                        {
                            label: 'Diastolic',
                            data: [70, 75, 80, 78, 82],
                            borderColor: '#3b82f6',
                            borderWidth: 1,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } }
                }
            });
        }
    }

    setupParticles() {
        const particlesContainer = document.getElementById('particles');
        const particleCount = 50;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random position
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            
            // Random size
            const size = Math.random() * 3 + 1;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            // Random opacity
            particle.style.opacity = Math.random() * 0.3 + 0.1;
            
            // Random animation delay
            particle.style.animationDelay = `${Math.random() * 20}s`;
            
            particlesContainer.appendChild(particle);
        }
    }

    simulateAPIStatus() {
        // Simulate API connection status
        setTimeout(() => {
            this.elements.genAiStatus.textContent = 'Active';
            this.elements.genAiStatus.parentElement.querySelector('.monitor-icon').className = 'monitor-icon success';
            
            // Update API status
            const apiStatus = this.elements.apiStatus;
            apiStatus.innerHTML = `
                <div class="status-indicator active"></div>
                <span>Connected to clinical databases</span>
                <div class="status-graph">
                    <div class="graph-bar"></div>
                    <div class="graph-bar"></div>
                    <div class="graph-bar"></div>
                    <div class="graph-bar"></div>
                    <div class="graph-bar"></div>
                </div>
            `;
        }, 2000);

        // Simulate Gen AI load
        setInterval(() => {
            const load = Math.floor(Math.random() * 40) + 60; // 60-100%
            this.elements.genAiLoad.style.width = `${load}%`;
            this.elements.genAiLoadValue.textContent = `${load}%`;
        }, 3000);
    }

    // Tab switching
    switchTab(button) {
        const tabId = button.dataset.tab;
        
        // Update active tab button
        this.elements.tabBtns.forEach(btn => {
            btn.classList.remove('active');
            btn.querySelector('.tab-indicator').style.width = '0';
        });
        button.classList.add('active');
        button.querySelector('.tab-indicator').style.width = '100%';
        
        // Show corresponding tab content
        this.elements.tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${tabId}Tab`) {
                content.classList.add('active');
            }
        });
    }

    // Report tab switching
    switchReportTab(button) {
        if (!button) return;
        const reportId = button.dataset.report;
        
        // Update active report tab
        this.elements.reportTabs.forEach(tab => {
            tab.classList.remove('active');
            tab.querySelector('.tab-indicator').style.width = '0';
        });
        button.classList.add('active');
        button.querySelector('.tab-indicator').style.width = '100%';
        
        // Show corresponding report section
        this.elements.reportSections.forEach(section => {
            section.classList.remove('active');
            if (section.id === `${reportId}Report`) {
                section.classList.add('active');
            }
        });
    }

    updateAgeCategory(age) {
        let category = '';
        if (age < 2) category = 'Infant';
        else if (age < 13) category = 'Child';
        else if (age < 20) category = 'Adolescent';
        else if (age < 65) category = 'Adult';
        else category = 'Senior';
        
        this.elements.ageCategory.textContent = category;
        
        // Update data points count
        this.updateDataPoints();
    }

    updatePainAssessment(painLevel) {
        this.elements.painValue.innerHTML = `<span>${painLevel.toFixed(1)}</span><small>/10</small>`;
        
        let description = '';
        if (painLevel <= 2) description = 'No pain - comfortable';
        else if (painLevel <= 4) description = 'Mild discomfort - manageable';
        else if (painLevel <= 6) description = 'Moderate pain - requires attention';
        else if (painLevel <= 8) description = 'Severe pain - immediate attention needed';
        else description = 'Worst pain possible - emergency';
        
        this.elements.painDescription.innerHTML = `<i class="fas fa-info-circle"></i><span>${description}</span>`;
    }

    updateVitalStatus(type, value) {
        let statusElement, normalRange, warningRange, criticalRange;
        
        switch(type) {
            case 'temp':
                statusElement = document.getElementById('tempStatus');
                normalRange = { min: 36.5, max: 37.5 };
                warningRange = { min: 35.5, max: 38.5 };
                break;
            case 'hr':
                statusElement = document.getElementById('hrStatus');
                normalRange = { min: 60, max: 100 };
                warningRange = { min: 50, max: 120 };
                break;
            case 'o2':
                statusElement = document.getElementById('o2Status');
                normalRange = { min: 95, max: 100 };
                warningRange = { min: 90, max: 94 };
                break;
            case 'rr':
                statusElement = document.getElementById('rrStatus');
                normalRange = { min: 12, max: 20 };
                warningRange = { min: 8, max: 24 };
                break;
        }
        
        if (!statusElement) return;
        
        const dot = statusElement.querySelector('.status-dot');
        const statusText = statusElement.querySelector('span:nth-child(2)');
        const rangeText = statusElement.querySelector('.status-range');
        
        let status = 'Normal';
        let dotClass = 'normal';
        
        if (value < warningRange.min || value > warningRange.max) {
            status = 'Critical';
            dotClass = 'critical';
        } else if (value < normalRange.min || value > normalRange.max) {
            status = 'Warning';
            dotClass = 'warning';
        }
        
        dot.className = `status-dot ${dotClass}`;
        statusText.textContent = status;
        
        if (rangeText) {
            rangeText.textContent = `(${normalRange.min}-${normalRange.max}${type === 'temp' ? '°C' : type === 'hr' ? ' bpm' : type === 'o2' ? '%' : '/min'})`;
        }
    }

    updateBPStatus() {
        const systolic = parseInt(this.elements.systolicBP.value);
        const diastolic = parseInt(this.elements.diastolicBP.value);
        const statusElement = document.getElementById('bpStatus');
        
        let status = '';
        let stage = '';
        let dotClass = 'normal';
        
        if (systolic < 90 || diastolic < 60) {
            status = 'Low';
            stage = 'Hypotension';
            dotClass = 'warning';
        } else if (systolic <= 120 && diastolic <= 80) {
            status = 'Normal';
            stage = 'Optimal';
            dotClass = 'normal';
        } else if (systolic <= 129 && diastolic <= 84) {
            status = 'Elevated';
            stage = 'Normal';
            dotClass = 'warning';
        } else if (systolic <= 139 && diastolic <= 89) {
            status = 'High';
            stage = 'Stage 1';
            dotClass = 'warning';
        } else if (systolic <= 159 && diastolic <= 99) {
            status = 'High';
            stage = 'Stage 2';
            dotClass = 'danger';
        } else {
            status = 'Critical';
            stage = 'Hypertensive Crisis';
            dotClass = 'critical';
        }
        
        const dot = statusElement.querySelector('.status-dot');
        const statusText = statusElement.querySelector('span:nth-child(2)');
        const stageText = statusElement.querySelector('.status-map');
        
        dot.className = `status-dot ${dotClass}`;
        statusText.textContent = `${status} (${systolic}/${diastolic} mmHg)`;
        stageText.textContent = `Stage: ${stage}`;
        
        // Update chart data
        if (this.bpChart) {
            const newData = this.bpChart.data.datasets[0].data.slice(1);
            newData.push(systolic);
            this.bpChart.data.datasets[0].data = newData;
            
            const newData2 = this.bpChart.data.datasets[1].data.slice(1);
            newData2.push(diastolic);
            this.bpChart.data.datasets[1].data = newData2;
            
            this.bpChart.update('none');
        }
    }

    updateDataPoints() {
        // Count selected symptoms
        const symptomCount = document.querySelectorAll('input[name="symptoms"]:checked').length;
        
        // Count vital signs (always 5)
        const vitalCount = 5;
        
        // Count demographics (age, gender, BMI, pain)
        const demoCount = 4;
        
        const total = symptomCount + vitalCount + demoCount;
        this.elements.dataPoints.textContent = total;
        
        // Update AI confidence based on data completeness
        const confidence = Math.min(98, 70 + (symptomCount * 2) + (total > 15 ? 10 : 0));
        this.elements.aiConfidence.textContent = `${confidence}%`;
    }

    updateSymptomsCount() {
        const count = document.querySelectorAll('input[name="symptoms"]:checked').length;
        this.elements.selectedSymptomsCount.textContent = `${count} symptoms selected`;
        this.updateDataPoints();
    }

    selectCommonSymptoms() {
        const commonSymptoms = ['fever', 'cough', 'fatigue', 'headache'];
        commonSymptoms.forEach(symptomId => {
            const checkbox = document.querySelector(`input[name="symptoms"][value="${symptomId}"]`);
            if (checkbox) checkbox.checked = true;
        });
        this.updateSymptomsCount();
        this.showToast('Common symptoms selected', 'success');
    }

    addCustomSymptom() {
        const input = this.elements.customSymptom;
        const value = input.value.trim();
        
        if (value) {
            const symptomsGrid = document.querySelector('.symptoms-grid');
            
            const chip = document.createElement('label');
            chip.className = 'symptom-chip';
            chip.innerHTML = `
                <input type="checkbox" name="symptoms" value="custom_${Date.now()}" checked>
                <span class="chip-content">
                    <span class="chip-icon">➕</span>
                    <span class="chip-label">${value}</span>
                </span>
            `;
            
            chip.querySelector('input').addEventListener('change', () => {
                this.updateSymptomsCount();
            });
            
            symptomsGrid.appendChild(chip);
            input.value = '';
            this.updateSymptomsCount();
            this.showToast('Custom symptom added', 'success');
        }
    }

    async analyzeClinicalData() {
        // Show loading state
        this.showLoading();
        
        // Disable analyze button
        this.elements.analyzeBtn.disabled = true;
        this.elements.analyzeBtn.classList.add('processing');
        
        try {
            // Simulate API call with progress
            await this.simulateAnalysis();
            
            // Generate reports
            await this.generateReports();
            
            // Show success
            this.showSuccess();
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError('Analysis failed. Please check your data and try again.');
        } finally {
            // Re-enable analyze button
            this.elements.analyzeBtn.disabled = false;
            this.elements.analyzeBtn.classList.remove('processing');
        }
    }

    simulateAnalysis() {
        return new Promise((resolve, reject) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                this.elements.analysisProgress.style.width = `${progress}%`;
                
                // Update processing steps
                const steps = document.querySelectorAll('.processing-steps .step');
                if (progress >= 25 && steps[0]) steps[0].classList.add('active');
                if (progress >= 50 && steps[1]) steps[1].classList.add('active');
                if (progress >= 75 && steps[2]) steps[2].classList.add('active');
                if (progress >= 90 && steps[3]) steps[3].classList.add('active');
                
                if (progress >= 100) {
                    clearInterval(interval);
                    setTimeout(resolve, 500);
                }
            }, 300);
        });
    }

    async generateReports() {
        // Collect patient data
        const patientData = this.collectPatientData();
        
        // Generate diagnosis report
        this.generateDiagnosisReport(patientData);
        
        // Generate clinical notes
        this.generateClinicalNotes(patientData);
        
        // Generate treatment plan
        this.generateTreatmentPlan(patientData);
        
        // Generate patient summary
        this.generatePatientSummary(patientData);
        
        // Generate risk analysis
        this.generateRiskAnalysis(patientData);
        
        // Switch to diagnosis tab
        this.switchReportTab(document.querySelector('[data-report="diagnosis"]'));
    }

    collectPatientData() {
        // Safety check for empty inputs
        const ageVal = this.elements.ageInput ? this.elements.ageInput.value : 45;
        const genderEl = document.querySelector('input[name="gender"]:checked');
        const genderVal = genderEl ? genderEl.value : 'unknown';

        return {
            // Demographics
            age: parseInt(ageVal),
            gender: genderVal,
            painLevel: parseFloat(this.elements.painSlider.value),
            
            // Vital signs
            temperature: parseFloat(this.elements.tempSlider.value),
            heartRate: parseInt(this.elements.hrSlider.value),
            bloodPressure: {
                systolic: parseInt(this.elements.systolicBP.value),
                diastolic: parseInt(this.elements.diastolicBP.value)
            },
            oxygen: parseInt(this.elements.o2Slider.value),
            respiratoryRate: parseInt(this.elements.rrSlider.value),
            
            // Symptoms
            symptoms: Array.from(document.querySelectorAll('input[name="symptoms"]:checked'))
                .map(input => input.value),
            
            // Timestamp
            timestamp: new Date().toISOString()
        };
    }

    generateDiagnosisReport(patientData) {
        const report = this.elements.diagnosisReport;
        
        // Simulate AI diagnosis based on symptoms
        const diagnoses = this.getDifferentialDiagnosis(patientData);
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-diagnoses"></i> AI Differential Diagnosis</h3>
                <span class="report-timestamp">Generated ${new Date().toLocaleString()}</span>
            </div>
            
            <div class="diagnosis-summary glass">
                <div class="diagnosis-confidence">
                    <div class="confidence-score">
                        <strong>${diagnoses.primary.confidence}%</strong>
                        <span>AI Confidence</span>
                    </div>
                    <div class="diagnosis-main">
                        <h4>Primary Diagnosis</h4>
                        <div class="diagnosis-item primary">
                            <i class="fas fa-stethoscope"></i>
                            <div>
                                <strong>${diagnoses.primary.name}</strong>
                                <p>${diagnoses.primary.description}</p>
                                <div class="diagnosis-tags">
                                    ${diagnoses.primary.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="differential-list">
                <h4>Differential Diagnoses</h4>
                ${diagnoses.differentials.map(diff => `
                    <div class="differential-item">
                        <div class="diff-header">
                            <strong>${diff.name}</strong>
                            <span class="diff-probability">${diff.probability}% probability</span>
                        </div>
                        <p>${diff.description}</p>
                        <div class="diff-actions">
                            <button class="btn-small" onclick="mediPatientAI.viewDiagnosisDetails('${diff.id}')">
                                <i class="fas fa-info-circle"></i> Details
                            </button>
                            <button class="btn-small" onclick="mediPatientAI.orderDiagnosticTest('${diff.id}')">
                                <i class="fas fa-vial"></i> Order Test
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="diagnostic-recommendations">
                <h4><i class="fas fa-lightbulb"></i> Diagnostic Recommendations</h4>
                <div class="recommendations-grid">
                    ${diagnoses.recommendations.map(rec => `
                        <div class="recommendation-card">
                            <i class="${rec.icon}"></i>
                            <div>
                                <strong>${rec.title}</strong>
                                <p>${rec.description}</p>
                                <span class="priority ${rec.priority}">${rec.priority.toUpperCase()} PRIORITY</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        report.classList.add('active');
    }

    getDifferentialDiagnosis(patientData) {
        // This is a simplified simulation
        // In a real app, this would call an AI API
        
        const commonDiagnoses = {
            pneumonia: {
                id: 'pneumonia',
                name: 'Community-Acquired Pneumonia',
                description: 'Acute lower respiratory tract infection with consolidation.',
                confidence: 85,
                tags: ['Respiratory', 'Infectious'],
                probability: 65
            },
            bronchitis: {
                id: 'bronchitis',
                name: 'Acute Bronchitis',
                description: 'Inflammation of the bronchial tubes.',
                confidence: 72,
                tags: ['Respiratory'],
                probability: 45
            },
            influenza: {
                id: 'influenza',
                name: 'Influenza',
                description: 'Viral respiratory infection with systemic symptoms.',
                confidence: 68,
                tags: ['Respiratory', 'Viral'],
                probability: 38
            },
            covid: {
                id: 'covid',
                name: 'COVID-19',
                description: 'SARS-CoV-2 viral infection.',
                confidence: 75,
                tags: ['Respiratory', 'Viral'],
                probability: 42
            }
        };
        
        // Determine primary diagnosis based on symptoms
        const symptoms = patientData.symptoms;
        let primary = commonDiagnoses.bronchitis;
        
        if (symptoms.includes('fever') && symptoms.includes('shortness_of_breath')) {
            primary = commonDiagnoses.pneumonia;
        } else if (symptoms.includes('fever') && symptoms.includes('cough')) {
            primary = commonDiagnoses.influenza;
        }
        
        return {
            primary: {
                name: primary.name,
                description: primary.description,
                confidence: primary.confidence,
                tags: primary.tags
            },
            differentials: [
                { ...commonDiagnoses.pneumonia, probability: symptoms.includes('shortness_of_breath') ? 75 : 30 },
                { ...commonDiagnoses.bronchitis, probability: symptoms.includes('cough') ? 70 : 25 },
                { ...commonDiagnoses.influenza, probability: symptoms.includes('fever') ? 65 : 20 },
                { ...commonDiagnoses.covid, probability: symptoms.includes('cough') && symptoms.includes('fever') ? 60 : 15 }
            ].sort((a, b) => b.probability - a.probability),
            recommendations: [
                {
                    icon: 'fas fa-x-ray',
                    title: 'Chest X-ray',
                    description: 'PA and lateral views to rule out pneumonia',
                    priority: 'high'
                },
                {
                    icon: 'fas fa-flask',
                    title: 'CBC with Differential',
                    description: 'Complete blood count to assess infection',
                    priority: 'medium'
                },
                {
                    icon: 'fas fa-virus',
                    title: 'Respiratory PCR Panel',
                    description: 'Test for influenza, COVID-19, RSV',
                    priority: 'medium'
                },
                {
                    icon: 'fas fa-procedures',
                    title: 'Pulse Oximetry Monitoring',
                    description: 'Continuous oxygen saturation monitoring',
                    priority: 'high'
                }
            ]
        };
    }

    generateClinicalNotes(patientData) {
        const report = this.elements.clinicalReport;
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-file-medical"></i> AI-Generated Clinical Notes</h3>
                <span class="report-timestamp">SOAP Format • ${new Date().toLocaleDateString()}</span>
            </div>
            
            <div class="soap-notes">
                <div class="soap-section">
                    <h4><span class="soap-label">S</span> Subjective</h4>
                    <div class="soap-content">
                        <p>${this.generateSubjectiveNotes(patientData)}</p>
                        <div class="symptoms-list">
                            ${patientData.symptoms.map(symptom => `
                                <span class="symptom-tag">${symptom.replace('_', ' ')}</span>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="soap-section">
                    <h4><span class="soap-label">O</span> Objective</h4>
                    <div class="soap-content">
                        ${this.generateObjectiveNotes(patientData)}
                    </div>
                </div>
                
                <div class="soap-section">
                    <h4><span class="soap-label">A</span> Assessment</h4>
                    <div class="soap-content">
                        ${this.generateAssessmentNotes(patientData)}
                    </div>
                </div>
                
                <div class="soap-section">
                    <h4><span class="soap-label">P</span> Plan</h4>
                    <div class="soap-content">
                        ${this.generatePlanNotes(patientData)}
                    </div>
                </div>
            </div>
            
            <div class="notes-actions">
                <button class="btn-primary" onclick="mediPatientAI.exportNotes()">
                    <i class="fas fa-download"></i> Export Notes
                </button>
                <button class="btn-secondary" onclick="mediPatientAI.copyToClipboard()">
                    <i class="fas fa-copy"></i> Copy to Clipboard
                </button>
                <button class="btn-secondary" onclick="mediPatientAI.shareNotes()">
                    <i class="fas fa-share"></i> Share with Team
                </button>
            </div>
        `;
        
        report.classList.add('active');
    }

    generateSubjectiveNotes(patientData) {
        const age = patientData.age;
        const gender = patientData.gender;
        const pain = patientData.painLevel;
        
        let notes = `${age}-year-old ${gender} presents with `;
        
        if (patientData.symptoms.length > 0) {
            notes += patientData.symptoms.map(s => s.replace('_', ' ')).join(', ');
        } else {
            notes += "no specific complaints";
        }
        
        notes += `. Reports pain level of ${pain}/10. `;
        
        if (pain > 7) {
            notes += "Describes pain as severe and debilitating. ";
        } else if (pain > 4) {
            notes += "Describes moderate discomfort affecting daily activities. ";
        } else {
            notes += "Describes mild discomfort, manageable with OTC medication. ";
        }
        
        return notes;
    }

    generateObjectiveNotes(patientData) {
        return `
            <div class="vitals-objective">
                <h5>Vital Signs:</h5>
                <div class="vitals-grid">
                    <div class="vital-item">
                        <span>Temperature</span>
                        <strong>${patientData.temperature}°C</strong>
                    </div>
                    <div class="vital-item">
                        <span>Heart Rate</span>
                        <strong>${patientData.heartRate} bpm</strong>
                    </div>
                    <div class="vital-item">
                        <span>Blood Pressure</span>
                        <strong>${patientData.bloodPressure.systolic}/${patientData.bloodPressure.diastolic} mmHg</strong>
                    </div>
                    <div class="vital-item">
                        <span>Oxygen Saturation</span>
                        <strong>${patientData.oxygen}%</strong>
                    </div>
                    <div class="vital-item">
                        <span>Respiratory Rate</span>
                        <strong>${patientData.respiratoryRate}/min</strong>
                    </div>
                </div>
            </div>
            <div class="physical-exam">
                <h5>Physical Exam Findings (AI Simulated):</h5>
                <ul>
                    <li>General: ${patientData.temperature > 37.5 ? 'Febrile, appears uncomfortable' : 'Appears well, in no acute distress'}</li>
                    <li>Cardiovascular: Regular rate and rhythm, no murmurs</li>
                    <li>Respiratory: ${patientData.respiratoryRate > 20 ? 'Tachypneic, clear breath sounds bilaterally' : 'Clear to auscultation bilaterally'}</li>
                    <li>HEENT: Normocephalic, atraumatic</li>
                </ul>
            </div>
        `;
    }

    generateAssessmentNotes(patientData) {
        return `
            <div class="assessment-content">
                <h5>Primary Assessment:</h5>
                <p>${patientData.age}-year-old with ${patientData.symptoms.length > 0 ? patientData.symptoms.map(s => s.replace('_', ' ')).join(', ') : 'no specific symptoms'}.</p>
                
                <h5>Differential Considerations:</h5>
                <ol>
                    <li><strong>Viral upper respiratory infection</strong> - Most likely given symptom constellation</li>
                    <li><strong>Community-acquired pneumonia</strong> - Rule out with chest imaging if symptoms persist</li>
                    <li><strong>Acute bronchitis</strong> - Consider if cough predominates</li>
                    <li><strong>COVID-19</strong> - PCR testing recommended</li>
                </ol>
                
                <div class="risk-assessment">
                    <h5>Risk Assessment:</h5>
                    <div class="risk-level ${patientData.oxygen < 95 ? 'high' : 'low'}">
                        <i class="fas fa-${patientData.oxygen < 95 ? 'exclamation-triangle' : 'shield-alt'}"></i>
                        <span>${patientData.oxygen < 95 ? 'Higher Risk - Requires close monitoring' : 'Low Risk - Can be managed outpatient'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    generatePlanNotes(patientData) {
        return `
            <div class="plan-content">
                <h5>Diagnostic Plan:</h5>
                <ul>
                    <li>Chest X-ray if respiratory symptoms persist > 48 hours</li>
                    <li>COVID-19 PCR testing</li>
                    <li>Influenza testing during season</li>
                    <li>Consider CBC if febrile > 48 hours</li>
                </ul>
                
                <h5>Therapeutic Plan:</h5>
                <ul>
                    <li>Supportive care: Rest, hydration, antipyretics PRN</li>
                    <li>Consider cough suppressant if cough affecting sleep</li>
                    <li>Antibiotics only if bacterial infection confirmed</li>
                </ul>
                
                <h5>Follow-up:</h5>
                <ul>
                    <li>Return if symptoms worsen or persist > 7 days</li>
                    <li>Seek emergency care if: Shortness of breath, chest pain, confusion</li>
                    <li>Follow-up in 48-72 hours for reassessment</li>
                </ul>
                
                <div class="patient-instructions">
                    <h5>Patient Instructions:</h5>
                    <p>Rest, increase fluid intake, monitor temperature, use OTC medications as directed for symptom relief.</p>
                </div>
            </div>
        `;
    }

    generateTreatmentPlan(patientData) {
        const report = this.elements.treatmentReport;
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-prescription"></i> Evidence-Based Treatment Plan</h3>
                <span class="report-timestamp">Guideline-based • ${new Date().toLocaleDateString()}</span>
            </div>
            
            <div class="treatment-plan">
                <div class="treatment-section">
                    <h4><i class="fas fa-pills"></i> Pharmacotherapy</h4>
                    <div class="medications-list">
                        ${this.generateMedications(patientData)}
                    </div>
                </div>
                
                <div class="treatment-section">
                    <h4><i class="fas fa-procedures"></i> Non-Pharmacological Interventions</h4>
                    <div class="interventions-list">
                        ${this.generateInterventions(patientData)}
                    </div>
                </div>
                
                <div class="treatment-section">
                    <h4><i class="fas fa-calendar-check"></i> Follow-up & Monitoring</h4>
                    <div class="followup-plan">
                        ${this.generateFollowupPlan(patientData)}
                    </div>
                </div>
                
                <div class="treatment-section">
                    <h4><i class="fas fa-exclamation-triangle"></i> Red Flags & When to Seek Care</h4>
                    <div class="red-flags">
                        ${this.generateRedFlags(patientData)}
                    </div>
                </div>
            </div>
            
            <div class="treatment-actions">
                <button class="btn-primary" onclick="mediPatientAI.prescribeMedications()">
                    <i class="fas fa-prescription-bottle"></i> Generate Prescriptions
                </button>
                <button class="btn-secondary" onclick="mediPatientAI.printTreatmentPlan()">
                    <i class="fas fa-print"></i> Print Plan
                </button>
            </div>
        `;
        
        report.classList.add('active');
    }

    generateMedications(patientData) {
        const meds = [];
        
        if (patientData.painLevel > 4) {
            meds.push({
                name: 'Acetaminophen',
                dose: '500-1000 mg',
                frequency: 'Q6H PRN',
                duration: '3-5 days',
                indication: 'Pain/Fever',
                class: 'Analgesic'
            });
        }
        
        if (patientData.symptoms.includes('cough')) {
            meds.push({
                name: 'Dextromethorphan',
                dose: '10-20 mg',
                frequency: 'Q6-8H PRN',
                duration: '5-7 days',
                indication: 'Cough suppression',
                class: 'Antitussive'
            });
        }
        
        if (patientData.temperature > 38) {
            meds.push({
                name: 'Ibuprofen',
                dose: '400 mg',
                frequency: 'Q6H PRN',
                duration: '3 days',
                indication: 'Fever/Inflammation',
                class: 'NSAID'
            });
        }
        
        return meds.map(med => `
            <div class="medication-card">
                <div class="med-header">
                    <strong>${med.name}</strong>
                    <span class="med-class">${med.class}</span>
                </div>
                <div class="med-details">
                    <div class="med-dose">
                        <span>Dose:</span>
                        <strong>${med.dose}</strong>
                    </div>
                    <div class="med-frequency">
                        <span>Frequency:</span>
                        <strong>${med.frequency}</strong>
                    </div>
                    <div class="med-duration">
                        <span>Duration:</span>
                        <strong>${med.duration}</strong>
                    </div>
                </div>
                <div class="med-indication">
                    <i class="fas fa-info-circle"></i>
                    <span>${med.indication}</span>
                </div>
            </div>
        `).join('');
    }

    generateInterventions(patientData) {
        const interventions = [
            {
                title: 'Rest & Hydration',
                description: 'Adequate rest and increased fluid intake (2-3L daily)',
                icon: 'fas fa-bed'
            },
            {
                title: 'Steam Inhalation',
                description: 'Humidified air to soothe respiratory tract',
                icon: 'fas fa-wind'
            },
            {
                title: 'Salt Water Gargle',
                description: 'Warm salt water gargles for throat irritation',
                icon: 'fas fa-tint'
            },
            {
                title: 'Nutrition Support',
                description: 'Balanced diet with emphasis on fruits and vegetables',
                icon: 'fas fa-apple-alt'
            }
        ];
        
        return interventions.map(int => `
            <div class="intervention-card">
                <i class="${int.icon}"></i>
                <div>
                    <strong>${int.title}</strong>
                    <p>${int.description}</p>
                </div>
            </div>
        `).join('');
    }

    generateFollowupPlan(patientData) {
        return `
            <div class="followup-timeline">
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <strong>24-48 Hours</strong>
                        <p>Reassess symptoms, check temperature trends</p>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <strong>3-5 Days</strong>
                        <p>Follow-up visit if symptoms persist or worsen</p>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <strong>1 Week</strong>
                        <p>Expected resolution of acute symptoms</p>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <strong>2 Weeks</strong>
                        <p>Complete recovery expected</p>
                    </div>
                </div>
            </div>
        `;
    }

    generateRedFlags(patientData) {
        const flags = [
            'Shortness of breath at rest',
            'Chest pain or pressure',
            'Confusion or altered mental status',
            'Inability to keep fluids down',
            'Fever > 39°C lasting > 48 hours',
            'Worsening symptoms despite treatment'
        ];
        
        return `
            <div class="flags-list">
                ${flags.map(flag => `
                    <div class="flag-item">
                        <i class="fas fa-exclamation-circle"></i>
                        <span>${flag}</span>
                    </div>
                `).join('')}
            </div>
            <div class="emergency-instructions">
                <strong><i class="fas fa-ambulance"></i> Emergency Instructions:</strong>
                <p>If any red flags appear, seek immediate medical attention or call emergency services.</p>
            </div>
        `;
    }

    generatePatientSummary(patientData) {
        const report = this.elements.patientReport;
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-user-circle"></i> Comprehensive Patient Summary</h3>
                <span class="report-timestamp">Complete clinical profile • ${new Date().toLocaleDateString()}</span>
            </div>
            
            <div class="patient-profile">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-user-injured"></i>
                    </div>
                    <div class="profile-info">
                        <h4>Clinical Summary</h4>
                        <p>${patientData.age}-year-old ${patientData.gender}</p>
                    </div>
                    <div class="profile-risk">
                        <span class="risk-badge ${patientData.oxygen < 95 ? 'high-risk' : 'low-risk'}">
                            ${patientData.oxygen < 95 ? 'Higher Risk' : 'Low Risk'}
                        </span>
                    </div>
                </div>
                
                <div class="profile-sections">
                    <div class="profile-section">
                        <h5><i class="fas fa-clipboard-list"></i> Current Presentation</h5>
                        <div class="presentation-details">
                            ${this.generatePresentationDetails(patientData)}
                        </div>
                    </div>
                    
                    <div class="profile-section">
                        <h5><i class="fas fa-heartbeat"></i> Vital Signs Summary</h5>
                        <div class="vitals-summary">
                            ${this.generateVitalsSummary(patientData)}
                        </div>
                    </div>
                    
                    <div class="profile-section">
                        <h5><i class="fas fa-chart-line"></i> Clinical Trajectory</h5>
                        <div class="trajectory-chart">
                            <canvas id="trajectoryChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    
                    <div class="profile-section">
                        <h5><i class="fas fa-file-medical-alt"></i> Clinical Documentation</h5>
                        <div class="document-links">
                            <button class="doc-link" onclick="mediPatientAI.exportNotes()">
                                <i class="fas fa-file-pdf"></i> Download Full Report
                            </button>
                            <button class="doc-link" onclick="mediPatientAI.shareNotes()">
                                <i class="fas fa-share-alt"></i> Share with Care Team
                            </button>
                            <button class="doc-link" onclick="mediPatientAI.printTreatmentPlan()">
                                <i class="fas fa-print"></i> Print Summary
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        report.classList.add('active');
        
        // Initialize trajectory chart
        setTimeout(() => this.initializeTrajectoryChart(), 100);
    }

    generatePresentationDetails(patientData) {
        return `
            <div class="presentation-grid">
                <div class="presentation-item">
                    <span>Chief Complaint</span>
                    <strong>${patientData.symptoms.length > 0 ? patientData.symptoms[0].replace('_', ' ') : 'General malaise'}</strong>
                </div>
                <div class="presentation-item">
                    <span>Duration</span>
                    <strong>Acute onset</strong>
                </div>
                <div class="presentation-item">
                    <span>Pain Level</span>
                    <strong>${patientData.painLevel}/10</strong>
                </div>
                <div class="presentation-item">
                    <span>Severity</span>
                    <strong>${patientData.painLevel > 7 ? 'Severe' : patientData.painLevel > 4 ? 'Moderate' : 'Mild'}</strong>
                </div>
            </div>
            <div class="symptoms-present">
                <h6>Presenting Symptoms:</h6>
                <div class="symptoms-tags">
                    ${patientData.symptoms.map(symptom => `
                        <span class="symptom-tag">${symptom.replace('_', ' ')}</span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateVitalsSummary(patientData) {
        const vitals = [
            { label: 'Temperature', value: `${patientData.temperature}°C`, status: patientData.temperature > 37.5 ? 'abnormal' : 'normal' },
            { label: 'Heart Rate', value: `${patientData.heartRate} bpm`, status: patientData.heartRate > 100 || patientData.heartRate < 60 ? 'abnormal' : 'normal' },
            { label: 'Blood Pressure', value: `${patientData.bloodPressure.systolic}/${patientData.bloodPressure.diastolic} mmHg`, status: patientData.bloodPressure.systolic > 140 || patientData.bloodPressure.diastolic > 90 ? 'abnormal' : 'normal' },
            { label: 'Oxygen', value: `${patientData.oxygen}%`, status: patientData.oxygen < 95 ? 'abnormal' : 'normal' },
            { label: 'Respiratory Rate', value: `${patientData.respiratoryRate}/min`, status: patientData.respiratoryRate > 20 ? 'abnormal' : 'normal' }
        ];
        
        return `
            <div class="vitals-grid-summary">
                ${vitals.map(vital => `
                    <div class="vital-summary ${vital.status}">
                        <span>${vital.label}</span>
                        <strong>${vital.value}</strong>
                        <i class="fas fa-${vital.status === 'normal' ? 'check-circle' : 'exclamation-circle'}"></i>
                    </div>
                `).join('')}
            </div>
            <div class="vitals-assessment">
                <p><i class="fas fa-${vitals.filter(v => v.status === 'abnormal').length > 0 ? 'exclamation-triangle' : 'check-circle'}"></i>
                ${vitals.filter(v => v.status === 'abnormal').length} of 5 vitals outside normal range</p>
            </div>
        `;
    }

    initializeTrajectoryChart() {
        const canvas = document.getElementById('trajectoryChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.trajectoryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: [
                    {
                        label: 'Symptom Severity',
                        data: [7, 6, 5, 4, 3, 2, 1],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 2,
                        tension: 0.4
                    },
                    {
                        label: 'Expected Recovery',
                        data: [7, 5, 4, 3, 2, 1, 1],
                        borderColor: '#10b981',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: { 
                        grid: { display: false }
                    },
                    y: { 
                        min: 0,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Severity (0-10)'
                        }
                    }
                }
            }
        });
    }

    generateRiskAnalysis(patientData) {
        const report = this.elements.riskReport;
        
        // Calculate risk scores
        const riskScores = this.calculateRiskScores(patientData);
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-exclamation-triangle"></i> Comprehensive Risk Analysis</h3>
                <span class="report-timestamp">Multi-factor assessment • ${new Date().toLocaleDateString()}</span>
            </div>
            
            <div class="risk-overview">
                <div class="risk-score-card">
                    <div class="risk-score ${riskScores.overall.level}">
                        <strong>${riskScores.overall.score}</strong>
                        <span>Overall Risk Score</span>
                    </div>
                    <div class="risk-level">
                        <h4>${riskScores.overall.level.toUpperCase()} RISK</h4>
                        <p>${riskScores.overall.recommendation}</p>
                    </div>
                </div>
            </div>
            
            <div class="risk-breakdown">
                <h4>Risk Factor Analysis</h4>
                <div class="risk-factors">
                    ${riskScores.factors.map(factor => `
                        <div class="risk-factor">
                            <div class="factor-header">
                                <span>${factor.name}</span>
                                <span class="factor-score ${factor.level}">${factor.score}</span>
                            </div>
                            <div class="factor-bar">
                                <div class="bar-fill ${factor.level}" style="width: ${factor.percentage}%"></div>
                            </div>
                            <p class="factor-description">${factor.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="risk-mitigation">
                <h4><i class="fas fa-shield-alt"></i> Risk Mitigation Strategies</h4>
                <div class="mitigation-strategies">
                    ${riskScores.mitigations.map(strategy => `
                        <div class="strategy-card">
                            <i class="${strategy.icon}"></i>
                            <div>
                                <strong>${strategy.title}</strong>
                                <p>${strategy.description}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="risk-monitoring">
                <h4><i class="fas fa-chart-line"></i> Monitoring Protocol</h4>
                <div class="monitoring-plan">
                    ${riskScores.monitoring.map(item => `
                        <div class="monitoring-item">
                            <i class="fas fa-${item.frequency === 'Continuous' ? 'heartbeat' : 'clock'}"></i>
                            <div>
                                <strong>${item.parameter}</strong>
                                <p>${item.frequency} • ${item.duration}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        report.classList.add('active');
    }

    calculateRiskScores(patientData) {
        // Simplified risk calculation
        let overallScore = 0;
        const factors = [];
        
        // Age risk
        const ageRisk = patientData.age >= 65 ? 3 : patientData.age >= 50 ? 2 : 1;
        factors.push({
            name: 'Age',
            score: ageRisk,
            level: ageRisk >= 3 ? 'high' : ageRisk >= 2 ? 'medium' : 'low',
            percentage: ageRisk * 25,
            description: patientData.age >= 65 ? 'Advanced age increases complication risk' : 'Age within low-risk range'
        });
        overallScore += ageRisk;
        
        // Vital signs risk
        const vitalRisk = 
            (patientData.temperature > 38 ? 2 : 0) +
            (patientData.heartRate > 100 ? 2 : 0) +
            (patientData.oxygen < 95 ? 3 : 0);
        
        factors.push({
            name: 'Vital Signs',
            score: Math.min(vitalRisk, 5),
            level: vitalRisk >= 4 ? 'high' : vitalRisk >= 2 ? 'medium' : 'low',
            percentage: Math.min(vitalRisk * 20, 100),
            description: vitalRisk >= 4 ? 'Multiple abnormal vitals require close monitoring' : 'Vital signs within acceptable range'
        });
        overallScore += vitalRisk;
        
        // Symptom severity risk
        const symptomRisk = 
            (patientData.painLevel > 7 ? 3 : patientData.painLevel > 4 ? 2 : 1) +
            (patientData.symptoms.length > 3 ? 2 : 0);
        
        factors.push({
            name: 'Symptom Severity',
            score: symptomRisk,
            level: symptomRisk >= 4 ? 'high' : symptomRisk >= 3 ? 'medium' : 'low',
            percentage: symptomRisk * 25,
            description: symptomRisk >= 4 ? 'Severe symptoms indicating significant illness' : 'Mild to moderate symptoms'
        });
        overallScore += symptomRisk;
        
        // Overall risk level
        const overallLevel = overallScore >= 8 ? 'high' : overallScore >= 5 ? 'medium' : 'low';
        const recommendation = 
            overallLevel === 'high' ? 'Consider hospital admission or close observation' :
            overallLevel === 'medium' ? 'Outpatient management with close follow-up' :
            'Standard outpatient care';
        
        return {
            overall: {
                score: overallScore,
                level: overallLevel,
                recommendation: recommendation
            },
            factors: factors,
            mitigations: [
                {
                    icon: 'fas fa-user-md',
                    title: 'Close Physician Follow-up',
                    description: 'Schedule follow-up within 24-48 hours for reassessment'
                },
                {
                    icon: 'fas fa-home',
                    title: 'Home Monitoring Setup',
                    description: 'Provide home monitoring equipment and instructions'
                },
                {
                    icon: 'fas fa-phone-alt',
                    title: 'Telemedicine Support',
                    description: '24/7 telemedicine access for symptom concerns'
                },
                {
                    icon: 'fas fa-ambulance',
                    title: 'Emergency Protocol',
                    description: 'Clear instructions for when to seek emergency care'
                }
            ],
            monitoring: [
                {
                    parameter: 'Temperature',
                    frequency: 'Q4-6H',
                    duration: 'Until afebrile for 24h'
                },
                {
                    parameter: 'Oxygen Saturation',
                    frequency: 'Continuous',
                    duration: 'First 48 hours'
                },
                {
                    parameter: 'Symptom Diary',
                    frequency: 'Daily',
                    duration: '7 days'
                },
                {
                    parameter: 'Physician Check-in',
                    frequency: 'Daily',
                    duration: '3 days'
                }
            ]
        };
    }

    loadTestCase(testCase) {
        // Load demographics
        this.elements.ageSlider.value = testCase.data.age;
        this.elements.ageInput.value = testCase.data.age;
        this.elements.ageValue.textContent = `${testCase.data.age} years`;
        this.updateAgeCategory(testCase.data.age);
        
        // Load gender
        document.querySelector(`input[name="gender"][value="${testCase.data.gender}"]`).checked = true;
        
        // Load vitals
        this.elements.tempSlider.value = testCase.data.temperature;
        this.elements.tempValue.textContent = `${testCase.data.temperature}°C`;
        this.updateVitalStatus('temp', testCase.data.temperature);
        
        this.elements.hrSlider.value = testCase.data.heartRate;
        this.elements.hrValue.textContent = `${testCase.data.heartRate} bpm`;
        this.updateVitalStatus('hr', testCase.data.heartRate);
        
        this.elements.sbpSlider.value = testCase.data.systolicBP;
        this.elements.dbpSlider.value = testCase.data.diastolicBP;
        this.elements.systolicBP.value = testCase.data.systolicBP;
        this.elements.diastolicBP.value = testCase.data.diastolicBP;
        this.updateBPStatus();
        
        this.elements.o2Slider.value = testCase.data.oxygen;
        this.elements.o2Value.textContent = `${testCase.data.oxygen}%`;
        this.updateVitalStatus('o2', testCase.data.oxygen);
        
        this.elements.rrSlider.value = testCase.data.respiratoryRate;
        this.elements.rrValue.textContent = `${testCase.data.respiratoryRate}/min`;
        this.updateVitalStatus('rr', testCase.data.respiratoryRate);
        
        // Load pain level
        this.elements.painSlider.value = testCase.data.painLevel;
        this.updatePainAssessment(testCase.data.painLevel);
        
        // Load symptoms
        document.querySelectorAll('input[name="symptoms"]').forEach(checkbox => {
            checkbox.checked = testCase.data.symptoms.includes(checkbox.value);
        });
        this.updateSymptomsCount();
        
        // Switch to symptoms tab
        const symptomsTab = document.querySelector('[data-tab="symptoms"]');
        this.switchTab(symptomsTab);
    }

    clearForm() {
        if (confirm('Are you sure you want to clear all form data?')) {
            // Reset demographics
            this.elements.ageSlider.value = 45;
            this.elements.ageInput.value = 45;
            this.elements.ageValue.textContent = '45 years';
            this.updateAgeCategory(45);
            
            // Reset gender
            const maleRadio = document.querySelector('input[name="gender"][value="male"]');
            if(maleRadio) maleRadio.checked = true;
            
            // Reset vitals to normal values
            const normalVitals = {
                temp: 37.0,
                hr: 75,
                sbp: 120,
                dbp: 80,
                o2: 98,
                rr: 16
            };
            
            this.elements.tempSlider.value = normalVitals.temp;
            this.elements.tempValue.textContent = `${normalVitals.temp}°C`;
            this.updateVitalStatus('temp', normalVitals.temp);
            
            this.elements.hrSlider.value = normalVitals.hr;
            this.elements.hrValue.textContent = `${normalVitals.hr} bpm`;
            this.updateVitalStatus('hr', normalVitals.hr);
            
            this.elements.sbpSlider.value = normalVitals.sbp;
            this.elements.dbpSlider.value = normalVitals.dbp;
            this.elements.systolicBP.value = normalVitals.sbp;
            this.elements.diastolicBP.value = normalVitals.dbp;
            this.updateBPStatus();
            
            this.elements.o2Slider.value = normalVitals.o2;
            this.elements.o2Value.textContent = `${normalVitals.o2}%`;
            this.updateVitalStatus('o2', normalVitals.o2);
            
            this.elements.rrSlider.value = normalVitals.rr;
            this.elements.rrValue.textContent = `${normalVitals.rr}/min`;
            this.updateVitalStatus('rr', normalVitals.rr);
            
            // Reset pain
            this.elements.painSlider.value = 3;
            this.updatePainAssessment(3);
            
            // Reset symptoms
            document.querySelectorAll('input[name="symptoms"]').forEach(checkbox => {
                checkbox.checked = false;
            });
            this.updateSymptomsCount();
            
            // Clear custom symptom
            this.elements.customSymptom.value = '';
            
            // Reset reports
            this.hideAllReports();
            this.showInitialState();
            
            this.showToast('Form cleared successfully', 'success');
        }
    }

    hideAllReports() {
        this.elements.reportSections.forEach(section => {
            section.classList.remove('active');
        });
    }

    showInitialState() {
        this.elements.initialState.classList.add('active');
        this.elements.loadingState.classList.remove('active');
        this.elements.errorState.classList.remove('active');
    }

    showLoading() {
        this.elements.initialState.classList.remove('active');
        this.elements.loadingState.classList.add('active');
        this.elements.errorState.classList.remove('active');
        
        // Reset progress
        this.elements.analysisProgress.style.width = '0%';
        document.querySelectorAll('.processing-steps .step').forEach(step => {
            step.classList.remove('active');
        });
    }

    showSuccess() {
        this.elements.loadingState.classList.remove('active');
        this.showToast('Analysis complete! Reports generated successfully.', 'success');
    }

    showError(message) {
        this.elements.loadingState.classList.remove('active');
        this.elements.errorState.classList.add('active');
        document.getElementById('errorMessage').textContent = message;
        this.showToast(message, 'error');
    }

    hideError() {
        this.elements.errorState.classList.remove('active');
    }

    toggleVoiceSearch() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showToast('Speech recognition not supported in your browser', 'warning');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        recognition.start();
        
        this.showToast('Listening... Speak your search query', 'info');
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.querySelector('.search-bar input').value = transcript;
            this.showToast(`Searching for: ${transcript}`, 'success');
        };
        
        recognition.onerror = (event) => {
            this.showToast('Speech recognition error', 'error');
        };
    }

    toggleVoiceInput() {
        this.showToast('Voice input would record clinical notes here', 'info');
    }

    async sendAIQuery() {
        const query = this.elements.aiQuery.value.trim();
        if (!query) return;
        
        // Add user message
        this.addAIMessage(query, 'user');
        this.elements.aiQuery.value = '';
        
        // Show typing indicator
        this.showAITyping();
        
        // Simulate AI response
        setTimeout(() => {
            this.hideAITyping();
            this.addAIResponse(query);
        }, 1500);
    }

    addAIMessage(message, type) {
        const messagesContainer = document.querySelector('.assistant-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${type === 'user' ? `<strong>You:</strong>` : `<strong>AI Assistant:</strong>`}
                <p>${message}</p>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showAITyping() {
        const messagesContainer = document.querySelector('.assistant-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-content">
                <strong>AI Assistant:</strong>
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideAITyping() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    addAIResponse(query) {
        const responses = {
            'symptoms': 'Based on the symptoms you described, I recommend considering these differential diagnoses...',
            'treatment': 'For this condition, evidence-based guidelines suggest...',
            'diagnosis': 'The clinical presentation suggests several possible diagnoses. Key considerations include...',
            'medication': 'Pharmacological management should be tailored based on...',
            'guideline': 'Current clinical guidelines recommend...',
            'default': 'I can help analyze clinical data, suggest differential diagnoses, and provide evidence-based recommendations. Please ask me about specific symptoms, treatments, or clinical guidelines.'
        };
        
        let response = responses.default;
        const lowerQuery = query.toLowerCase();
        
        if (lowerQuery.includes('symptom')) response = responses.symptoms;
        else if (lowerQuery.includes('treat') || lowerQuery.includes('medic')) response = responses.treatment;
        else if (lowerQuery.includes('diagnos')) response = responses.diagnosis;
        else if (lowerQuery.includes('guideline')) response = responses.guideline;
        
        this.addAIMessage(response, 'ai');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="${icons[type]}"></i>
            <div class="toast-content">
                <h4>${type.charAt(0).toUpperCase() + type.slice(1)}</h4>
                <p>${message}</p>
            </div>
            <button class="close-toast">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
        
        // Close button
        toast.querySelector('.close-toast').addEventListener('click', () => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        });
    }

    // ============================================================
    //  UPDATED PUBLIC METHODS FOR ACTIONS & PDF
    // ============================================================

    viewDiagnosisDetails(diagnosisId) {
        this.showToast(`Viewing details for diagnosis: ${diagnosisId}`, 'info');
    }

    orderDiagnosticTest(testId) {
        this.showToast(`Ordering diagnostic test: ${testId}`, 'success');
    }

    // --- REAL PDF EXPORT FUNCTIONALITY ---
    exportNotes() {
        this.showToast('Generating Clinical Notes PDF...', 'info');
        
        const patientData = this.collectPatientData();
        const diagnoses = this.getDifferentialDiagnosis(patientData);

        this.generatePDF('Clinical Notes', patientData, diagnoses);
    }

    printTreatmentPlan() {
        this.showToast('Generating Treatment Plan PDF...', 'info');
        
        const patientData = this.collectPatientData();
        const diagnoses = this.getDifferentialDiagnosis(patientData);
        
        this.generatePDF('Treatment Plan', patientData, diagnoses);
    }

    // --- PDF GENERATOR HELPER ---
    generatePDF(reportType, patientData, diagnoses) {
        // Ensure library is loaded
        if (!window.jspdf) {
            this.showToast('PDF Library not loaded', 'error');
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        
        // 1. Header
        doc.setFillColor(41, 98, 255); // Blue header
        doc.rect(0, 0, pageWidth, 40, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.text("MediPatient AI", 14, 20);
        
        doc.setFontSize(12);
        doc.text(`Report Type: ${reportType}`, 14, 32);
        doc.text(`Date: ${new Date().toLocaleDateString()}`, pageWidth - 14, 32, { align: 'right' });

        // 2. Patient Info
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(12);
        doc.text(`Patient Age: ${patientData.age}`, 14, 50);
        doc.text(`Gender: ${patientData.gender}`, 14, 56);
        doc.text(`Vitals: BP ${patientData.bloodPressure.systolic}/${patientData.bloodPressure.diastolic} | HR ${patientData.heartRate} | Temp ${patientData.temperature}°C`, 14, 62);

        // 3. Primary Diagnosis Section
        doc.setFontSize(16);
        doc.setTextColor(41, 98, 255);
        doc.text("Primary Diagnosis", 14, 75);
        
        doc.setFontSize(12);
        doc.setTextColor(0, 0, 0);
        doc.text(`${diagnoses.primary.name} (${diagnoses.primary.confidence}% Confidence)`, 14, 85);
        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(diagnoses.primary.description, 14, 91);

        // 4. Differential Diagnosis Table
        if (diagnoses.differentials && diagnoses.differentials.length > 0) {
            const tableBody = diagnoses.differentials.map(d => [
                d.name,
                `${d.probability}%`,
                d.tags.join(', ')
            ]);

            doc.autoTable({
                startY: 100,
                head: [['Differential Diagnosis', 'Probability', 'Category']],
                body: tableBody,
                theme: 'grid',
                headStyles: { fillColor: [41, 98, 255] }
            });
        }

        // 5. Recommendations / Plan
        const finalY = doc.lastAutoTable ? doc.lastAutoTable.finalY : 120;
        doc.setFontSize(16);
        doc.setTextColor(41, 98, 255);
        doc.text("Clinical Recommendations", 14, finalY + 15);

        const recs = diagnoses.recommendations.map(r => `• ${r.priority.toUpperCase()}: ${r.title} - ${r.description}`);
        
        doc.setFontSize(10);
        doc.setTextColor(0);
        doc.text(recs, 14, finalY + 25);

        // Save
        doc.save(`MediPatient_${reportType.replace(' ', '_')}.pdf`);
        this.showToast('PDF Downloaded successfully', 'success');
    }

    copyToClipboard() {
        this.showToast('Copied to clipboard!', 'success');
    }

    shareNotes() {
        this.showToast('Sharing with care team...', 'info');
    }

    prescribeMedications() {
        this.showToast('Generating prescriptions...', 'info');
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mediPatientAI = new MediPatientAI();
});