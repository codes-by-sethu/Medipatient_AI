// MediPatient AI - Complete Fixed Version
// Version 6.2 - Updated Test Cases to Match ML Model

class MediPatientAI {
    constructor() {
        this.apiClient = new MediPatientAPIClient();
        this.currentPatientData = null;
        this.currentAPIResult = null;
        this.patientHistory = JSON.parse(localStorage.getItem('patientHistory') || '[]');
        this.medicalSearchHistory = [];
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupApp());
        } else {
            this.setupApp();
        }
    }

    setupApp() {
        try {
            this.setupDOM();
            this.setupEventListeners();
            this.setupTestCases();
            this.setupSymptoms();
            this.initializeCharts();
            this.setupParticles();
            this.simulateAPIStatus();
            this.loadSearchHistory();
            
            const hash = window.location.hash.replace('#', '');
            if (hash && ['dashboard', 'patients', 'reports'].includes(hash)) {
                this.switchMainSection(hash);
            } else {
                this.switchMainSection('dashboard');
            }
            
            console.log('MediPatient AI initialized successfully');
            
            setTimeout(() => {
                this.showToast('MediPatient AI Ready. Enter patient data to begin analysis.', 'info');
            }, 1000);
            
        } catch (error) {
            console.error('Failed to initialize MediPatient AI:', error);
            this.showToast('Application initialization failed. Please refresh.', 'error');
        }
    }

    setupDOM() {
        this.elements = {
            clinicalForm: document.getElementById('clinicalForm'),
            ageSlider: document.getElementById('ageSlider'),
            ageInput: document.getElementById('age'),
            ageValue: document.getElementById('ageValue'),
            ageCategory: document.getElementById('ageCategory'),
            painSlider: document.getElementById('painSlider'),
            painValue: document.getElementById('painValue'),
            painDescription: document.getElementById('painDescription'),
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
            
            analyzeBtn: document.getElementById('analyzeBtn'),
            clearForm: document.getElementById('clearForm'),
            showTestCases: document.getElementById('showTestCases'),
            closePanel: document.getElementById('closePanel'),
            retryBtn: document.getElementById('retryBtn'),
            exportReportBtn: document.getElementById('exportReport'),
            printReportBtn: document.getElementById('printReport'),
            
            loader: document.getElementById('loader'),
            dataPoints: document.getElementById('dataPoints'),
            aiConfidence: document.getElementById('aiConfidence'),
            initialState: document.getElementById('initialState'),
            loadingState: document.getElementById('loadingState'),
            errorState: document.getElementById('errorState'),
            analysisProgress: document.getElementById('analysisProgress'),
            
            diagnosisReport: document.getElementById('diagnosisReport'),
            clinicalReport: document.getElementById('clinicalReport'),
            treatmentReport: document.getElementById('treatmentReport'),
            patientReport: document.getElementById('patientReport'),
            riskReport: document.getElementById('riskReport'),
            
            tabBtns: document.querySelectorAll('.tab-btn'),
            tabContents: document.querySelectorAll('.tab-content'),
            reportTabs: document.querySelectorAll('.report-tab'),
            reportSections: document.querySelectorAll('.report-section'),
            
            selectAllBtn: document.getElementById('selectAllBtn'),
            customSymptom: document.getElementById('customSymptom'),
            addSymptom: document.getElementById('addSymptom'),
            selectedSymptomsCount: document.getElementById('selectedSymptomsCount'),
            symptomSeverity: document.getElementById('symptomSeverity'),
            
            testCasesPanel: document.getElementById('testCasesPanel'),
            
            genAiStatus: document.getElementById('genAiStatus'),
            genAiLoad: document.getElementById('genAiLoad'),
            genAiLoadValue: document.getElementById('genAiLoadValue'),
            apiStatus: document.getElementById('apiStatus'),
            
            aiModelChart: document.getElementById('aiModelChart'),
            bpChart: document.getElementById('bpChart')?.querySelector('canvas'),
            
            dashboardSection: document.querySelector('.dashboard-grid').parentElement,
            patientsSection: document.getElementById('patientsSection'),
            reportsSection: document.getElementById('reportsSection'),
            refreshReports: document.getElementById('refreshReports'),
            
            historyEntries: document.getElementById('historyEntries') || 
                          document.querySelector('#patientsSection .history-entries'),
            totalEntries: document.getElementById('totalEntries'),
            lastEntry: document.getElementById('lastEntry'),
            avgEntries: document.getElementById('avgEntries'),
            clearHistory: document.getElementById('clearHistory'),
            totalPatients: document.getElementById('totalPatients'),
            lastAssessment: document.getElementById('lastAssessment'),
            avgSeverity: document.getElementById('avgSeverity'),
            
            reportsList: document.getElementById('reportsList'),
            refreshReportsBtn: document.getElementById('refreshReports')
        };
    }

    setupEventListeners() {
        this.elements.tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target));
        });

        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.switchMainSection(section);
                window.location.hash = section;
            });
        });

        this.elements.reportTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.switchReportTab(e.target));
        });

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

        this.elements.painSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.updatePainAssessment(value);
        });

        this.setupVitalSliders();

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

        this.elements.analyzeBtn.addEventListener('click', () => this.analyzeClinicalData());
        this.elements.clearForm.addEventListener('click', () => this.clearForm());

        this.elements.showTestCases.addEventListener('click', () => {
            this.elements.testCasesPanel.classList.add('active');
        });

        this.elements.closePanel.addEventListener('click', () => {
            this.elements.testCasesPanel.classList.remove('active');
        });

        this.elements.retryBtn.addEventListener('click', () => {
            this.hideError();
            this.analyzeClinicalData();
        });

        if (this.elements.exportReportBtn) {
            this.elements.exportReportBtn.addEventListener('click', () => {
                if (this.currentAPIResult && this.currentAPIResult.pdf_report_url) {
                    window.open(this.currentAPIResult.pdf_report_url, '_blank');
                    this.showToast('Downloading PDF report...', 'info');
                } else {
                    this.showToast('No PDF report available. Please run analysis first.', 'warning');
                }
            });
        }

        if (this.elements.printReportBtn) {
            this.elements.printReportBtn.addEventListener('click', () => {
                if (this.currentAPIResult && this.currentAPIResult.pdf_report_url) {
                    const win = window.open(this.currentAPIResult.pdf_report_url, '_blank');
                    setTimeout(() => {
                        if (win) win.print();
                    }, 1000);
                } else {
                    this.showToast('No report available for printing', 'warning');
                }
            });
        }

        if (this.elements.refreshReportsBtn) {
            this.elements.refreshReportsBtn.addEventListener('click', () => {
                this.loadReportsFromAPI();
            });
        }

        if (this.elements.clearHistory) {
            this.elements.clearHistory.addEventListener('click', () => this.clearAllHistory());
        }

        // FIX: Add Patient Hub button listeners
        document.getElementById('refreshPatients')?.addEventListener('click', () => {
            this.loadPatientHistory();
        });

        document.getElementById('clearAllHistory')?.addEventListener('click', () => {
            this.clearAllHistory();
        });

        this.elements.selectAllBtn?.addEventListener('click', () => this.selectCommonSymptoms());
        this.elements.addSymptom?.addEventListener('click', () => this.addCustomSymptom());

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.test-cases-panel') && 
                !e.target.closest('#showTestCases')) {
                this.elements.testCasesPanel?.classList.remove('active');
            }
        });
    }

    setupVitalSliders() {
        this.elements.tempSlider?.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.elements.tempValue.textContent = `${value.toFixed(1)}°C`;
            this.updateVitalStatus('temp', value);
        });

        this.elements.hrSlider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.hrValue.textContent = `${value} bpm`;
            this.updateVitalStatus('hr', value);
        });

        this.elements.sbpSlider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.systolicBP.value = value;
            this.updateBPStatus();
        });

        this.elements.dbpSlider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.diastolicBP.value = value;
            this.updateBPStatus();
        });

        this.elements.o2Slider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.o2Value.textContent = `${value}%`;
            this.updateVitalStatus('o2', value);
        });

        this.elements.rrSlider?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.elements.rrValue.textContent = `${value}/min`;
            this.updateVitalStatus('rr', value);
        });
    }

    setupTestCases() {
        const testCases = [
            {
                id: 'sepsis',
                title: '⚠️ SEPSIS / SEPTIC SHOCK',
                description: 'High fever, tachycardia, hypotension, hypoxia - Critical case',
                icon: 'fas fa-skull-crossbones',
                color: 'critical',
                data: {
                    age: 65,
                    gender: 'male',
                    temperature: 39.5,
                    heartRate: 115,
                    systolicBP: 85,
                    diastolicBP: 50,
                    oxygenSaturation: 88,
                    respiratoryRate: 28,
                    painScore: 8,
                    symptoms: ['fever', 'shortness_of_breath', 'fatigue', 'confusion']
                }
            },
            {
                id: 'healthy',
                title: '✅ NORMAL CHECKUP',
                description: 'All vitals within normal limits',
                icon: 'fas fa-user-check',
                color: 'success',
                data: {
                    age: 30,
                    gender: 'female',
                    temperature: 37.0,
                    heartRate: 70,
                    systolicBP: 120,
                    diastolicBP: 80,
                    oxygenSaturation: 99,
                    respiratoryRate: 16,
                    painScore: 2,
                    symptoms: []
                }
            },
            {
                id: 'hypertension',
                title: '💔 HYPERTENSIVE CRISIS',
                description: 'Extreme hypertension without fever',
                icon: 'fas fa-heart-pulse',
                color: 'warning',
                data: {
                    age: 55,
                    gender: 'male',
                    temperature: 36.8,
                    heartRate: 95,
                    systolicBP: 210,
                    diastolicBP: 120,
                    oxygenSaturation: 96,
                    respiratoryRate: 20,
                    painScore: 6,
                    symptoms: ['chest_pain', 'headache', 'dizziness']
                }
            },
            {
                id: 'pneumonia',
                title: '🫁 COMMUNITY-ACQUIRED PNEUMONIA',
                description: 'Fever, productive cough, dyspnea, crackles',
                icon: 'fas fa-lungs-virus',
                color: 'warning',
                data: {
                    age: 65,
                    gender: 'male',
                    temperature: 39.2,
                    heartRate: 105,
                    systolicBP: 130,
                    diastolicBP: 85,
                    oxygenSaturation: 89,
                    respiratoryRate: 24,
                    painScore: 7,
                    symptoms: ['fever', 'cough', 'shortness_of_breath', 'fatigue']
                }
            },
            {
                id: 'mi',
                title: '⚡ ACUTE MYOCARDIAL INFARCTION',
                description: 'Chest pain, diaphoresis, nausea, ST elevation',
                icon: 'fas fa-heart-crack',
                color: 'critical',
                data: {
                    age: 58,
                    gender: 'male',
                    temperature: 37.2,
                    heartRate: 95,
                    systolicBP: 150,
                    diastolicBP: 95,
                    oxygenSaturation: 96,
                    respiratoryRate: 20,
                    painScore: 9,
                    symptoms: ['chest_pain', 'nausea', 'dizziness', 'fatigue']
                }
            },
            {
                id: 'trauma',
                title: '🩸 TRAUMA / BLOOD LOSS',
                description: 'Tachycardia, hypotension, no fever',
                icon: 'fas fa-user-injured',
                color: 'critical',
                data: {
                    age: 25,
                    gender: 'male',
                    temperature: 36.5,
                    heartRate: 130,
                    systolicBP: 80,
                    diastolicBP: 50,
                    oxygenSaturation: 98,
                    respiratoryRate: 22,
                    painScore: 8,
                    symptoms: ['fatigue', 'dizziness']
                }
            }
        ];

        const grid = document.querySelector('.test-cases-grid');
        if (!grid) return;
        
        grid.innerHTML = '';

        testCases.forEach(testCase => {
            const card = document.createElement('div');
            card.className = `test-case-card ${testCase.color}`;
            card.dataset.case = testCase.id;
            
            card.innerHTML = `
                <div class="case-icon ${testCase.color}">
                    <i class="${testCase.icon}"></i>
                </div>
                <h4>${testCase.title}</h4>
                <p>${testCase.description}</p>
                <div class="case-vitals">
                    <span>Temp: ${testCase.data.temperature}°C</span>
                    <span>HR: ${testCase.data.heartRate}</span>
                    <span>BP: ${testCase.data.systolicBP}/${testCase.data.diastolicBP}</span>
                    <span>O2: ${testCase.data.oxygenSaturation}%</span>
                </div>
                <button class="load-case-btn ${testCase.color}">
                    <i class="fas fa-upload"></i> Load Scenario
                </button>
            `;

            card.querySelector('.load-case-btn').addEventListener('click', () => {
                this.loadTestCase(testCase);
                this.elements.testCasesPanel.classList.remove('active');
                this.showToast(`Loaded ${testCase.title} scenario`, 'success');
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
            { id: 'confusion', label: 'Confusion', icon: '🧠' },
            { id: 'vomiting', label: 'Vomiting', icon: '🤮' },
            { id: 'diarrhea', label: 'Diarrhea', icon: '💩' },
            { id: 'rash', label: 'Rash', icon: '🔴' },
            { id: 'joint_pain', label: 'Joint Pain', icon: '🦵' }
        ];

        const grid = document.querySelector('.symptoms-grid');
        if (!grid) return;
        
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

    loadTestCase(testCase) {
        if (this.elements.ageSlider) {
            this.elements.ageSlider.value = testCase.data.age;
            this.elements.ageInput.value = testCase.data.age;
            this.elements.ageValue.textContent = `${testCase.data.age} years`;
            this.updateAgeCategory(testCase.data.age);
        }
        
        const genderRadio = document.querySelector(`input[name="gender"][value="${testCase.data.gender}"]`);
        if (genderRadio) genderRadio.checked = true;
        
        if (this.elements.tempSlider) {
            this.elements.tempSlider.value = testCase.data.temperature;
            this.elements.tempValue.textContent = `${testCase.data.temperature}°C`;
            this.updateVitalStatus('temp', testCase.data.temperature);
        }
        
        if (this.elements.hrSlider) {
            this.elements.hrSlider.value = testCase.data.heartRate;
            this.elements.hrValue.textContent = `${testCase.data.heartRate} bpm`;
            this.updateVitalStatus('hr', testCase.data.heartRate);
        }
        
        if (this.elements.sbpSlider && this.elements.dbpSlider) {
            this.elements.sbpSlider.value = testCase.data.systolicBP;
            this.elements.dbpSlider.value = testCase.data.diastolicBP;
            this.elements.systolicBP.value = testCase.data.systolicBP;
            this.elements.diastolicBP.value = testCase.data.diastolicBP;
            this.updateBPStatus();
        }
        
        if (this.elements.o2Slider) {
            this.elements.o2Slider.value = testCase.data.oxygenSaturation;
            this.elements.o2Value.textContent = `${testCase.data.oxygenSaturation}%`;
            this.updateVitalStatus('o2', testCase.data.oxygenSaturation);
        }
        
        if (this.elements.rrSlider) {
            this.elements.rrSlider.value = testCase.data.respiratoryRate;
            this.elements.rrValue.textContent = `${testCase.data.respiratoryRate}/min`;
            this.updateVitalStatus('rr', testCase.data.respiratoryRate);
        }
        
        if (this.elements.painSlider) {
            this.elements.painSlider.value = testCase.data.painScore;
            this.updatePainAssessment(testCase.data.painScore);
        }
        
        document.querySelectorAll('input[name="symptoms"]').forEach(checkbox => {
            const symptomKey = checkbox.value;
            checkbox.checked = testCase.data.symptoms.includes(symptomKey);
        });
        this.updateSymptomsCount();
        
        const symptomsTab = document.querySelector('[data-tab="symptoms"]');
        if (symptomsTab) this.switchTab(symptomsTab);
    }

    collectPatientData() {
        const selectedSymptoms = Array.from(document.querySelectorAll('input[name="symptoms"]:checked'))
            .map(input => input.value);
        
        const symptomsMap = {};
        const allSymptoms = [
            'fever', 'cough', 'shortness_of_breath', 'fatigue', 'chest_pain',
            'nausea', 'dizziness', 'confusion', 'vomiting', 'diarrhea',
            'rash', 'joint_pain', 'headache'
        ];
        
        allSymptoms.forEach(symptom => {
            symptomsMap[symptom] = selectedSymptoms.includes(symptom) ? true : false;
        });
        
        return {
            age: parseInt(this.elements.ageInput?.value) || 45,
            gender: document.querySelector('input[name="gender"]:checked')?.value || 'unknown',
            temperature: parseFloat(this.elements.tempSlider?.value) || 37.0,
            heartRate: parseInt(this.elements.hrSlider?.value) || 80,
            systolicBP: parseInt(this.elements.systolicBP?.value) || 120,
            diastolicBP: parseInt(this.elements.diastolicBP?.value) || 80,
            respiratoryRate: parseInt(this.elements.rrSlider?.value) || 16,
            oxygenSaturation: parseInt(this.elements.o2Slider?.value) || 98,
            painScore: parseFloat(this.elements.painSlider?.value) || 3,
            fever: symptomsMap.fever || false,
            cough: symptomsMap.cough || false,
            shortness_of_breath: symptomsMap.shortness_of_breath || false,
            fatigue: symptomsMap.fatigue || false,
            chest_pain: symptomsMap.chest_pain || false,
            nausea: symptomsMap.nausea || false,
            dizziness: symptomsMap.dizziness || false,
            confusion: symptomsMap.confusion || false,
            headache: symptomsMap.headache || false,
            medical_history: [],
            allergies: [],
            medications: []
        };
    }

    async analyzeClinicalData() {
        this.showLoading();
        
        if (this.elements.analyzeBtn) {
            this.elements.analyzeBtn.disabled = true;
            this.elements.analyzeBtn.classList.add('processing');
        }
        
        try {
            const status = await this.apiClient.checkAPIStatus();
            
            if (status.status !== 'online') {
                throw new Error('Backend API is offline. Please ensure the Python server is running.');
            }
            
            const patientData = this.collectPatientData();
            const analysisPromise = this.apiClient.predict(patientData);
            const progressPromise = this.simulateAnalysis();
            
            const [apiResult] = await Promise.all([analysisPromise, progressPromise]);
            
            if (apiResult.status === 'error') {
                throw new Error(apiResult.message || 'Analysis failed');
            }
            
            this.currentPatientData = patientData;
            this.currentAPIResult = apiResult;
            this.saveToPatientHistory(patientData, apiResult);
            await this.generateReportsFromAPI(apiResult, patientData);
            this.showSuccess();
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError(error.message || 'Analysis failed. Please check your data and try again.');
        } finally {
            if (this.elements.analyzeBtn) {
                this.elements.analyzeBtn.disabled = false;
                this.elements.analyzeBtn.classList.remove('processing');
            }
        }
    }

    simulateAnalysis() {
        return new Promise((resolve) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                if (this.elements.analysisProgress) {
                    this.elements.analysisProgress.style.width = `${progress}%`;
                }
                
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

    async generateReportsFromAPI(apiResult, patientData) {
        const normalizedResult = this.normalizeAPIResult(apiResult);
        
        this.currentAPIResult = normalizedResult;
        this.currentPatientData = patientData;
        
        if (this.elements.initialState) {
            this.elements.initialState.classList.remove('active');
            this.elements.initialState.style.display = 'none';
        }
        
        this.clearAllSections();
        this.generateDiagnosisReportFromAPI(normalizedResult, patientData);
        this.generateClinicalNotesFromAPI(normalizedResult, patientData);
        this.generateTreatmentPlanFromAPI(normalizedResult, patientData);
        this.generatePatientSummaryFromAPI(normalizedResult, patientData);
        this.generateRiskAnalysisFromAPI(normalizedResult, patientData);
        
        this.hideLoading();
        this.showResults();
        
        setTimeout(() => {
            const diagnosisTab = document.querySelector('[data-report="diagnosis"]');
            if (diagnosisTab) this.switchReportTab(diagnosisTab);
        }, 100);
    }

    normalizeAPIResult(apiResult) {
        if (!apiResult) return {};
        
        let confidence = apiResult.confidence || 'medium';
        if (typeof confidence === 'number') {
            if (confidence >= 0.7) confidence = 'high';
            else if (confidence >= 0.5) confidence = 'medium';
            else confidence = 'low';
        }
        
        let severity = apiResult.severity || 'moderate';
        if (typeof severity === 'number') {
            if (severity < 0.3) severity = 'mild';
            else if (severity < 0.6) severity = 'moderate';
            else if (severity < 0.8) severity = 'severe';
            else severity = 'critical';
        }
        
        let urgency = apiResult.urgency || 'routine';
        if (typeof urgency === 'string') {
            urgency = urgency.toLowerCase();
        } else {
            urgency = 'routine';
        }
        
        return {
            status: apiResult.status || 'success',
            primary_diagnosis: apiResult.primary_diagnosis || 'Unknown Diagnosis',
            confidence: confidence,
            severity: severity,
            urgency: urgency,
            reasoning: apiResult.reasoning || 'Analysis provided by ML Model.',
            treatment_plan: apiResult.treatment_plan || {},
            pdf_report_url: apiResult.pdf_report_url || null,
            source: apiResult.source || 'ML Model',
            severity_score: apiResult.severity_score || 5
        };
    }

    generateDiagnosisReportFromAPI(apiResult, patientData) {
        const report = this.elements.diagnosisReport;
        if (!report) return;
        
        const confidence = apiResult.confidence || 'medium';
        const severity = apiResult.severity || 'moderate';
        const urgency = apiResult.urgency || 'routine';
        
        let confidencePercentage = '75%';
        if (confidence === 'high') confidencePercentage = '85-95%';
        else if (confidence === 'medium') confidencePercentage = '70-84%';
        else if (confidence === 'low') confidencePercentage = '50-69%';
        
        const hasGemini = apiResult.source && apiResult.source.includes('Gemini');
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-diagnoses"></i> AI Differential Diagnosis</h3>
                <span class="report-timestamp">Generated ${new Date().toLocaleString()}</span>
                <div class="api-badge">
                    <i class="fas fa-server"></i> Real ML Model
                    ${hasGemini ? '<span class="gen-ai-badge"><i class="fas fa-robot"></i> Gemini Enhanced</span>' : ''}
                    ${apiResult.pdf_report_url ? '<span class="pdf-badge"><i class="fas fa-file-pdf"></i> PDF Available</span>' : ''}
                </div>
            </div>
            
            <div class="diagnosis-summary glass">
                <div class="diagnosis-confidence">
                    <div class="confidence-score">
                        <strong>${confidencePercentage}</strong>
                        <span>AI Confidence (${confidence})</span>
                    </div>
                    <div class="diagnosis-main">
                        <h4>Primary Diagnosis</h4>
                        <div class="diagnosis-item primary">
                            <i class="fas fa-stethoscope"></i>
                            <div>
                                <strong>${apiResult.primary_diagnosis}</strong>
                                <p>${apiResult.reasoning}</p>
                                <div class="diagnosis-tags">
                                    <span class="tag severity-${severity}">Severity: ${severity}</span>
                                    <span class="tag urgency-${urgency}">Urgency: ${urgency}</span>
                                    <span class="tag">${hasGemini ? 'ML + Gemini' : 'ML Model'}</span>
                                    ${apiResult.pdf_report_url ? '<span class="tag">PDF Report</span>' : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            ${apiResult.treatment_plan && Object.keys(apiResult.treatment_plan).length > 0 ? `
                <div class="differential-section">
                    <h4><i class="fas fa-prescription"></i> Treatment Plan</h4>
                    <div class="treatment-plan-grid">
                        ${Object.entries(apiResult.treatment_plan).map(([key, value]) => `
                            <div class="treatment-item">
                                <div class="treatment-header">
                                    <i class="fas fa-${this.getTreatmentIcon(key)}"></i>
                                    <h5>${this.formatTreatmentKey(key)}</h5>
                                </div>
                                <div class="treatment-content">
                                    <p>${value}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${apiResult.pdf_report_url ? `
                <div class="pdf-download-section glass">
                    <i class="fas fa-file-pdf"></i>
                    <div>
                        <strong>PDF Report Generated</strong>
                        <p>Complete clinical report with SOAP notes and treatment plan</p>
                    </div>
                    <button class="btn-primary" onclick="window.open('${apiResult.pdf_report_url}', '_blank')">
                        <i class="fas fa-download"></i> Download PDF
                    </button>
                </div>
            ` : ''}
        `;
        
        report.classList.add('active');
    }

    generateClinicalNotesFromAPI(apiResult, patientData) {
        const report = this.elements.clinicalReport;
        if (!report) return;
        
        const symptomsList = [];
        if (patientData.fever) symptomsList.push('Fever');
        if (patientData.cough) symptomsList.push('Cough');
        if (patientData.shortness_of_breath) symptomsList.push('Shortness of breath');
        if (patientData.fatigue) symptomsList.push('Fatigue');
        if (patientData.chest_pain) symptomsList.push('Chest pain');
        if (patientData.headache) symptomsList.push('Headache');
        if (patientData.nausea) symptomsList.push('Nausea');
        if (patientData.dizziness) symptomsList.push('Dizziness');
        
        const severity = apiResult.severity || 'moderate';
        const urgency = apiResult.urgency || 'routine';
        const confidence = apiResult.confidence || 'medium';
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-file-medical"></i> Clinical Documentation</h3>
                <span class="report-timestamp">SOAP Format • ${new Date().toLocaleDateString()}</span>
                <div class="api-badge">
                    ${apiResult.source && apiResult.source.includes('Gemini') ? 
                        '<i class="fas fa-robot"></i> Gemini AI Generated' : 
                        '<i class="fas fa-brain"></i> ML Generated'}
                </div>
            </div>
            
            <div class="soap-notes">
                <div class="soap-section">
                    <h4><span class="soap-label">S</span> Subjective</h4>
                    <div class="soap-content">
                        <p>${patientData.age}-year-old ${patientData.gender} presenting with ${symptomsList.length} symptoms including ${symptomsList.join(', ')}. Pain score: ${patientData.painScore}/10.</p>
                    </div>
                </div>
                
                <div class="soap-section">
                    <h4><span class="soap-label">O</span> Objective</h4>
                    <div class="soap-content">
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
                                    <strong>${patientData.systolicBP}/${patientData.diastolicBP} mmHg</strong>
                                </div>
                                <div class="vital-item">
                                    <span>Respiratory Rate</span>
                                    <strong>${patientData.respiratoryRate}/min</strong>
                                </div>
                                <div class="vital-item">
                                    <span>O₂ Saturation</span>
                                    <strong>${patientData.oxygenSaturation}%</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="soap-section">
                    <h4><span class="soap-label">A</span> Assessment</h4>
                    <div class="soap-content">
                        <p><strong>${apiResult.primary_diagnosis}</strong></p>
                        <p>${apiResult.reasoning}</p>
                        <div class="assessment-details">
                            <div class="detail-row">
                                <span>Severity:</span>
                                <strong class="severity-${severity}">${severity}</strong>
                            </div>
                            <div class="detail-row">
                                <span>Urgency:</span>
                                <strong class="urgency-${urgency}">${urgency}</strong>
                            </div>
                            <div class="detail-row">
                                <span>Confidence:</span>
                                <strong>${confidence}</strong>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="soap-section">
                    <h4><span class="soap-label">P</span> Plan</h4>
                    <div class="soap-content">
                        ${apiResult.treatment_plan && Object.keys(apiResult.treatment_plan).length > 0 ? `
                            <h5>Treatment Plan:</h5>
                            <ul>
                                ${Object.entries(apiResult.treatment_plan).map(([key, value]) => `
                                    <li><strong>${this.formatTreatmentKey(key)}:</strong> ${value}</li>
                                `).join('')}
                            </ul>
                        ` : '<p>Follow-up with healthcare provider for further evaluation and management.</p>'}
                    </div>
                </div>
            </div>
        `;
        
        report.classList.add('active');
    }

    updateAgeCategory(age) {
        let category = '';
        if (age < 2) category = 'Infant';
        else if (age < 13) category = 'Child';
        else if (age < 20) category = 'Adolescent';
        else if (age < 65) category = 'Adult';
        else category = 'Senior';
        
        if (this.elements.ageCategory) {
            this.elements.ageCategory.textContent = category;
        }
        
        this.updateDataPoints();
    }

    updatePainAssessment(painLevel) {
        if (!this.elements.painValue) return;
        
        this.elements.painValue.innerHTML = `<span>${painLevel.toFixed(1)}</span><small>/10</small>`;
        
        let description = '';
        if (painLevel <= 2) description = 'No pain - comfortable';
        else if (painLevel <= 4) description = 'Mild discomfort - manageable';
        else if (painLevel <= 6) description = 'Moderate pain - requires attention';
        else if (painLevel <= 8) description = 'Severe pain - immediate attention needed';
        else description = 'Worst pain possible - emergency';
        
        if (this.elements.painDescription) {
            this.elements.painDescription.innerHTML = `<i class="fas fa-info-circle"></i><span>${description}</span>`;
        }
    }

    updateVitalStatus(type, value) {
        let statusElement, normalRange, warningRange;
        
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
        if (!this.elements.systolicBP || !this.elements.diastolicBP) return;
        
        const systolic = parseInt(this.elements.systolicBP.value);
        const diastolic = parseInt(this.elements.diastolicBP.value);
        const statusElement = document.getElementById('bpStatus');
        
        if (!statusElement) return;
        
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
        
        if (dot) dot.className = `status-dot ${dotClass}`;
        if (statusText) statusText.textContent = `${status} (${systolic}/${diastolic} mmHg)`;
        if (stageText) stageText.textContent = `Stage: ${stage}`;
        
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
        const symptomCount = document.querySelectorAll('input[name="symptoms"]:checked').length;
        const vitalCount = 5;
        const demoCount = 4;
        const total = symptomCount + vitalCount + demoCount;
        
        if (this.elements.dataPoints) {
            this.elements.dataPoints.textContent = total;
        }
        
        const confidence = Math.min(98, 70 + (symptomCount * 2) + (total > 15 ? 10 : 0));
        if (this.elements.aiConfidence) {
            this.elements.aiConfidence.textContent = `${confidence}%`;
        }
    }

    updateSymptomsCount() {
        const count = document.querySelectorAll('input[name="symptoms"]:checked').length;
        if (this.elements.selectedSymptomsCount) {
            this.elements.selectedSymptomsCount.textContent = `${count} symptoms selected`;
        }
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
        if (!input) return;
        
        const value = input.value.trim();
        
        if (value) {
            const symptomsGrid = document.querySelector('.symptoms-grid');
            if (!symptomsGrid) return;
            
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

    switchMainSection(section) {
        if (this.elements.dashboardSection) this.elements.dashboardSection.style.display = 'none';
        if (this.elements.patientsSection) this.elements.patientsSection.style.display = 'none';
        if (this.elements.reportsSection) this.elements.reportsSection.style.display = 'none';
        
        switch(section) {
            case 'dashboard':
                if (this.elements.dashboardSection) {
                    this.elements.dashboardSection.style.display = 'block';
                }
                break;
            case 'patients':
                if (this.elements.patientsSection) {
                    this.elements.patientsSection.style.display = 'block';
                    this.loadPatientHistory();
                }
                break;
            case 'reports':
                if (this.elements.reportsSection) {
                    this.elements.reportsSection.style.display = 'block';
                    this.loadReportsFromAPI();
                }
                break;
        }
        
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const navItem = document.querySelector(`[data-section="${section}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
    }

    switchTab(button) {
        const tabId = button.dataset.tab;
        
        this.elements.tabBtns.forEach(btn => {
            btn.classList.remove('active');
            const indicator = btn.querySelector('.tab-indicator');
            if (indicator) indicator.style.width = '0';
        });
        button.classList.add('active');
        const indicator = button.querySelector('.tab-indicator');
        if (indicator) indicator.style.width = '100%';
        
        this.elements.tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${tabId}Tab`) {
                content.classList.add('active');
            }
        });
    }

    switchReportTab(button) {
        if (!button) return;
        const reportId = button.dataset.report;
        
        this.elements.reportTabs.forEach(tab => {
            tab.classList.remove('active');
            const indicator = tab.querySelector('.tab-indicator');
            if (indicator) indicator.style.width = '0';
        });
        button.classList.add('active');
        const indicator = button.querySelector('.tab-indicator');
        if (indicator) indicator.style.width = '100%';
        
        this.elements.reportSections.forEach(section => {
            section.classList.remove('active');
            if (section.id === `${reportId}Report`) {
                section.classList.add('active');
            }
        });
    }

    clearForm() {
        if (confirm('Are you sure you want to clear all form data?')) {
            if (this.elements.ageSlider) {
                this.elements.ageSlider.value = 45;
                this.elements.ageInput.value = 45;
                this.elements.ageValue.textContent = '45 years';
                this.updateAgeCategory(45);
            }
            
            const maleRadio = document.querySelector('input[name="gender"][value="male"]');
            if(maleRadio) maleRadio.checked = true;
            
            const normalVitals = {
                temp: 37.0,
                hr: 75,
                sbp: 120,
                dbp: 80,
                o2: 98,
                rr: 16
            };
            
            if (this.elements.tempSlider) {
                this.elements.tempSlider.value = normalVitals.temp;
                this.elements.tempValue.textContent = `${normalVitals.temp}°C`;
                this.updateVitalStatus('temp', normalVitals.temp);
            }
            
            if (this.elements.hrSlider) {
                this.elements.hrSlider.value = normalVitals.hr;
                this.elements.hrValue.textContent = `${normalVitals.hr} bpm`;
                this.updateVitalStatus('hr', normalVitals.hr);
            }
            
            if (this.elements.sbpSlider && this.elements.dbpSlider) {
                this.elements.sbpSlider.value = normalVitals.sbp;
                this.elements.dbpSlider.value = normalVitals.dbp;
                this.elements.systolicBP.value = normalVitals.sbp;
                this.elements.diastolicBP.value = normalVitals.dbp;
                this.updateBPStatus();
            }
            
            if (this.elements.o2Slider) {
                this.elements.o2Slider.value = normalVitals.o2;
                this.elements.o2Value.textContent = `${normalVitals.o2}%`;
                this.updateVitalStatus('o2', normalVitals.o2);
            }
            
            if (this.elements.rrSlider) {
                this.elements.rrSlider.value = normalVitals.rr;
                this.elements.rrValue.textContent = `${normalVitals.rr}/min`;
                this.updateVitalStatus('rr', normalVitals.rr);
            }
            
            if (this.elements.painSlider) {
                this.elements.painSlider.value = 3;
                this.updatePainAssessment(3);
            }
            
            document.querySelectorAll('input[name="symptoms"]').forEach(checkbox => {
                checkbox.checked = false;
            });
            this.updateSymptomsCount();
            
            if (this.elements.customSymptom) {
                this.elements.customSymptom.value = '';
            }
            
            this.hideAllReports();
            this.showInitialState();
            
            this.showToast('Form cleared successfully', 'success');
        }
    }

    showLoading() {
        if (this.elements.initialState) {
            this.elements.initialState.classList.remove('active');
            this.elements.initialState.style.display = 'none';
        }
        
        if (this.elements.loadingState) {
            this.elements.loadingState.classList.add('active');
            this.elements.loadingState.style.display = 'block';
        }
        
        if (this.elements.errorState) {
            this.elements.errorState.classList.remove('active');
            this.elements.errorState.style.display = 'none';
        }
    }

    hideLoading() {
        if (this.elements.loadingState) {
            this.elements.loadingState.classList.remove('active');
            this.elements.loadingState.style.display = 'none';
        }
    }

    showSuccess() {
        this.showToast('Analysis complete! Reports generated successfully.', 'success');
    }

    showError(message) {
        this.hideLoading();
        
        if (this.elements.errorState) {
            this.elements.errorState.classList.add('active');
            this.elements.errorState.style.display = 'block';
            const errorMessage = document.getElementById('errorMessage');
            if (errorMessage) errorMessage.textContent = message;
        }
        
        if (this.elements.initialState) {
            this.elements.initialState.style.display = 'none';
        }
        
        this.showToast(message, 'error');
    }

    hideError() {
        if (this.elements.errorState) {
            this.elements.errorState.classList.remove('active');
            this.elements.errorState.style.display = 'none';
        }
    }

    hideAllReports() {
        this.elements.reportSections.forEach(section => {
            section.classList.remove('active');
        });
    }

    showInitialState() {
        if (this.elements.initialState) {
            this.elements.initialState.classList.add('active');
            this.elements.initialState.style.display = 'block';
        }
        if (this.elements.loadingState) this.elements.loadingState.classList.remove('active');
        if (this.elements.errorState) this.elements.errorState.classList.remove('active');
    }

    showResults() {
        const reportsContainer = document.querySelector('.report-content');
        if (reportsContainer) {
            reportsContainer.classList.add('active');
        }
    }

    clearAllSections() {
        const sections = [
            'diagnosisReport',
            'clinicalReport', 
            'treatmentReport',
            'patientReport',
            'riskReport'
        ];
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.innerHTML = '';
                section.classList.remove('active');
            }
        });
        
        if (this.elements.initialState) this.elements.initialState.classList.remove('active');
        if (this.elements.loadingState) this.elements.loadingState.classList.remove('active');
        if (this.elements.errorState) this.elements.errorState.classList.remove('active');
    }

    saveToPatientHistory(patientData, apiResult) {
        const normalizedResult = this.normalizeAPIResult(apiResult);
        
        const historyEntry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            data: patientData,
            result: {
                diagnosis: normalizedResult.primary_diagnosis,
                confidence: normalizedResult.confidence,
                severity: normalizedResult.severity,
                urgency: normalizedResult.urgency,
                pdf_url: normalizedResult.pdf_report_url,
                reasoning: normalizedResult.reasoning
            }
        };
        
        this.patientHistory.unshift(historyEntry);
        
        if (this.patientHistory.length > 50) {
            this.patientHistory = this.patientHistory.slice(0, 50);
        }
        
        localStorage.setItem('patientHistory', JSON.stringify(this.patientHistory));
        
        if (window.location.hash === '#patients') {
            this.updatePatientStats();
            this.loadPatientHistory();
        }
    }

    // FIXED: Single loadPatientHistory function
    loadPatientHistory() {
        const patientHistoryContainer = document.getElementById('patientHistoryEntries');
        if (!patientHistoryContainer) {
            console.error('❌ Cannot find patientHistoryEntries element!');
            return;
        }
        
        this.updatePatientStats();
        
        if (this.patientHistory.length === 0) {
            patientHistoryContainer.innerHTML = `
                <div class="empty-history">
                    <i class="fas fa-history"></i>
                    <h4>No Patient History Yet</h4>
                    <p>Patient assessments will be saved here automatically</p>
                    <p class="small">Run an analysis from the Clinical Dashboard to start building history</p>
                </div>
            `;
            return;
        }
        
        patientHistoryContainer.innerHTML = this.patientHistory.map((entry, index) => `
            <div class="history-entry glass">
                <div class="entry-header">
                    <div class="entry-icon">
                        <i class="fas fa-user-injured"></i>
                    </div>
                    <div class="entry-info">
                        <strong>Assessment #${this.patientHistory.length - index}</strong>
                        <span class="entry-time">${this.formatDateTime(entry.timestamp)}</span>
                    </div>
                    <div class="entry-diagnosis">
                        <span class="diagnosis-tag">${entry.result.diagnosis}</span>
                    </div>
                </div>
                <div class="entry-details">
                    <div class="detail-item">
                        <span>Age:</span>
                        <strong>${entry.data.age} years</strong>
                    </div>
                    <div class="detail-item">
                        <span>Symptoms:</span>
                        <strong>${this.countSymptoms(entry.data)}</strong>
                    </div>
                    <div class="detail-item">
                        <span>Severity:</span>
                        <strong class="severity-${entry.result.severity}">${entry.result.severity}</strong>
                    </div>
                </div>
                <div class="entry-actions">
                    <button class="btn-small view-btn" onclick="mediPatientAI.loadHistoryEntry(${index})">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                    <button class="btn-small delete-btn" onclick="mediPatientAI.deleteHistoryEntry(${index})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    countSymptoms(patientData) {
        let count = 0;
        const symptomFields = ['fever', 'cough', 'shortness_of_breath', 'fatigue', 'chest_pain', 
                              'headache', 'nausea', 'dizziness', 'vomiting', 'diarrhea', 'rash', 'joint_pain'];
        symptomFields.forEach(symptom => {
            if (patientData[symptom] === true) count++;
        });
        return count;
    }

    updatePatientStats() {
        if (this.elements.totalEntries) {
            this.elements.totalEntries.textContent = this.patientHistory.length;
        }
        
        if (this.elements.lastEntry) {
            if (this.patientHistory.length > 0) {
                const lastEntry = this.patientHistory[0];
                this.elements.lastEntry.textContent = this.formatRelativeTime(lastEntry.timestamp);
            } else {
                this.elements.lastEntry.textContent = 'None';
            }
        }
        
        if (this.elements.avgEntries) {
            if (this.patientHistory.length > 0) {
                const oldestEntry = this.patientHistory[this.patientHistory.length - 1];
                const newestEntry = this.patientHistory[0];
                
                const oldestDate = new Date(oldestEntry.timestamp);
                const newestDate = new Date(newestEntry.timestamp);
                
                const diffMonths = (newestDate.getFullYear() - oldestDate.getFullYear()) * 12 + 
                                  (newestDate.getMonth() - oldestDate.getMonth());
                
                if (diffMonths > 0) {
                    const avgPerMonth = (this.patientHistory.length / diffMonths).toFixed(1);
                    this.elements.avgEntries.textContent = avgPerMonth;
                } else {
                    this.elements.avgEntries.textContent = this.patientHistory.length;
                }
            } else {
                this.elements.avgEntries.textContent = '0';
            }
        }
        
        // Update Patient Hub stats
        const totalPatientsElement = document.getElementById('totalPatients');
        if (totalPatientsElement) {
            totalPatientsElement.textContent = this.patientHistory.length;
        }
        
        const lastAssessmentElement = document.getElementById('lastAssessment');
        if (lastAssessmentElement) {
            if (this.patientHistory.length > 0) {
                lastAssessmentElement.textContent = this.formatRelativeTime(this.patientHistory[0].timestamp);
            } else {
                lastAssessmentElement.textContent = 'None';
            }
        }
        
        const avgSeverityElement = document.getElementById('avgSeverity');
        if (avgSeverityElement && this.patientHistory.length > 0) {
            const severityMap = { 'critical': 4, 'severe': 3, 'moderate': 2, 'low': 1, 'unknown': 0 };
            let totalScore = 0;
            let count = 0;
            
            this.patientHistory.forEach(entry => {
                const score = severityMap[entry.result?.severity] || 0;
                if (score > 0) {
                    totalScore += score;
                    count++;
                }
            });
            
            if (count > 0) {
                const avgScore = totalScore / count;
                let severityText = '';
                if (avgScore >= 3.5) severityText = 'Critical';
                else if (avgScore >= 2.5) severityText = 'High';
                else if (avgScore >= 1.5) severityText = 'Medium';
                else severityText = 'Low';
                
                avgSeverityElement.textContent = severityText;
            } else {
                avgSeverityElement.textContent = 'N/A';
            }
        }
    }

    clearAllHistory() {
        if (this.patientHistory.length === 0) {
            this.showToast('No history to clear', 'info');
            return;
        }
        
        if (confirm('Are you sure you want to delete ALL patient history? This action cannot be undone.')) {
            this.patientHistory = [];
            localStorage.removeItem('patientHistory');
            this.loadPatientHistory();
            this.showToast('All patient history cleared successfully', 'success');
        }
    }

    loadHistoryEntry(index) {
        if (index >= 0 && index < this.patientHistory.length) {
            const entry = this.patientHistory[index];
            
            this.loadPatientDataIntoForm(entry.data);
            
            if (entry.result) {
                this.currentAPIResult = this.normalizeAPIResult(entry.result);
                this.currentPatientData = entry.data;
                this.generateReportsFromAPI(entry.result, entry.data);
            }
            
            this.switchMainSection('dashboard');
            
            this.showToast(`Loaded patient data from ${this.formatRelativeTime(entry.timestamp)}`, 'success');
        }
    }

    deleteHistoryEntry(index) {
        if (confirm('Are you sure you want to delete this history entry?')) {
            this.patientHistory.splice(index, 1);
            localStorage.setItem('patientHistory', JSON.stringify(this.patientHistory));
            this.loadPatientHistory();
            this.showToast('History entry deleted successfully', 'success');
        }
    }

    loadPatientDataIntoForm(data) {
        if (this.elements.ageSlider) {
            this.elements.ageSlider.value = data.age;
            this.elements.ageInput.value = data.age;
            this.elements.ageValue.textContent = `${data.age} years`;
            this.updateAgeCategory(data.age);
        }
        
        const genderRadio = document.querySelector(`input[name="gender"][value="${data.gender}"]`);
        if (genderRadio) genderRadio.checked = true;
        
        if (this.elements.tempSlider) {
            this.elements.tempSlider.value = data.temperature;
            this.elements.tempValue.textContent = `${data.temperature}°C`;
            this.updateVitalStatus('temp', data.temperature);
        }
        
        if (this.elements.hrSlider) {
            this.elements.hrSlider.value = data.heartRate;
            this.elements.hrValue.textContent = `${data.heartRate} bpm`;
            this.updateVitalStatus('hr', data.heartRate);
        }
        
        if (this.elements.sbpSlider && this.elements.dbpSlider) {
            this.elements.sbpSlider.value = data.systolicBP;
            this.elements.dbpSlider.value = data.diastolicBP;
            this.elements.systolicBP.value = data.systolicBP;
            this.elements.diastolicBP.value = data.diastolicBP;
            this.updateBPStatus();
        }
        
        if (this.elements.o2Slider) {
            this.elements.o2Slider.value = data.oxygenSaturation;
            this.elements.o2Value.textContent = `${data.oxygenSaturation}%`;
            this.updateVitalStatus('o2', data.oxygenSaturation);
        }
        
        if (this.elements.rrSlider) {
            this.elements.rrSlider.value = data.respiratoryRate;
            this.elements.rrValue.textContent = `${data.respiratoryRate}/min`;
            this.updateVitalStatus('rr', data.respiratoryRate);
        }
        
        if (this.elements.painSlider) {
            this.elements.painSlider.value = data.painScore;
            this.updatePainAssessment(data.painScore);
        }
        
        document.querySelectorAll('input[name="symptoms"]').forEach(checkbox => {
            const symptomKey = checkbox.value;
            checkbox.checked = data[symptomKey] === true;
        });
        this.updateSymptomsCount();
    }

    async loadReportsFromAPI() {
        if (!this.elements.reportsList) return;
        
        try {
            this.elements.reportsList.innerHTML = '<div class="loading-reports"><i class="fas fa-spinner fa-spin"></i> Loading reports...</div>';
            
            const response = await fetch('/api/get-reports');
            const result = await response.json();
            
            if (!response.ok || result.status === 'error' || result.count === 0) {
                this.elements.reportsList.innerHTML = `
                    <div class="empty-reports">
                        <i class="fas fa-file-medical"></i>
                        <h4>No Reports Found</h4>
                        <p>Run a clinical analysis to generate your first report</p>
                        <p class="small">Reports are automatically saved as PDF files</p>
                    </div>
                `;
                return;
            }
            
            this.elements.reportsList.innerHTML = result.reports.map((report, index) => `
                <div class="report-item glass">
                    <div class="report-icon">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="report-info">
                        <strong>Clinical Report #${index + 1}</strong>
                        <p>${report.filename}</p>
                        <div class="report-meta">
                            <span><i class="fas fa-calendar"></i> ${this.formatDateTime(report.created)}</span>
                            <span><i class="fas fa-file"></i> ${this.formatFileSize(report.size)}</span>
                        </div>
                    </div>
                    <div class="report-actions">
                        <button class="btn-small view-btn" onclick="window.open('${report.download_url}', '_blank')">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn-small download-btn" onclick="window.open('${report.download_url}', '_blank')">
                            <i class="fas fa-download"></i> Download
                        </button>
                        <button class="btn-small delete-btn" onclick="mediPatientAI.deleteReport('${report.filename}', ${index})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error loading reports:', error);
            this.elements.reportsList.innerHTML = `
                <div class="error-reports">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Error Loading Reports</h4>
                    <p>${error.message}</p>
                    <button class="btn-small" onclick="mediPatientAI.loadReportsFromAPI()">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    async deleteReport(filename, index) {
        if (!confirm(`Are you sure you want to delete report: ${filename}?`)) return;
        
        try {
            const response = await fetch(`/api/delete-report/${filename}`, { 
                method: 'DELETE' 
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                this.showToast('Report deleted successfully', 'success');
                this.loadReportsFromAPI();
            } else {
                throw new Error(result.message || 'Failed to delete report');
            }
            
        } catch (error) {
            console.error('Error deleting report:', error);
            this.showToast(`Failed to delete report: ${error.message}`, 'error');
        }
    }

    initializeCharts() {
        if (this.elements.aiModelChart) {
            const ctx = this.elements.aiModelChart.getContext('2d');
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
                    plugins: { legend: { display: false } },
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

        if (this.elements.bpChart) {
            const bpCtx = this.elements.bpChart.getContext('2d');
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
        if (!particlesContainer) return;
        
        const particleCount = 50;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            
            const size = Math.random() * 3 + 1;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            particle.style.opacity = Math.random() * 0.3 + 0.1;
            particle.style.animationDelay = `${Math.random() * 20}s`;
            
            particlesContainer.appendChild(particle);
        }
    }

    simulateAPIStatus() {
        setTimeout(() => {
            if (this.elements.genAiStatus) {
                this.elements.genAiStatus.textContent = 'Active';
                const monitorIcon = this.elements.genAiStatus.parentElement.querySelector('.monitor-icon');
                if (monitorIcon) monitorIcon.className = 'monitor-icon success';
            }
            
            if (this.elements.apiStatus) {
                this.elements.apiStatus.innerHTML = `
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
            }
        }, 2000);

        if (this.elements.genAiLoad) {
            setInterval(() => {
                const load = Math.floor(Math.random() * 40) + 60;
                this.elements.genAiLoad.style.width = `${load}%`;
                if (this.elements.genAiLoadValue) {
                    this.elements.genAiLoadValue.textContent = `${load}%`;
                }
            }, 3000);
        }
    }

    loadSearchHistory() {
        this.medicalSearchHistory = JSON.parse(localStorage.getItem('medicalSearchHistory') || '[]');
    }

    getTreatmentIcon(key) {
        const iconMap = {
            'medication': 'pills',
            'monitoring': 'heartbeat',
            'lifestyle': 'apple-alt',
            'followup': 'calendar-check',
            'referral': 'user-md',
            'tests': 'vial',
            'emergency': 'ambulance'
        };
        return iconMap[key.toLowerCase()] || 'check-circle';
    }

    formatTreatmentKey(key) {
        return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    formatDateTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return 'Invalid date';
        }
    }

    formatRelativeTime(timestamp) {
        try {
            const now = new Date();
            const date = new Date(timestamp);
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            
            return this.formatDateTime(timestamp);
        } catch (e) {
            return 'Unknown time';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    generateTreatmentPlanFromAPI(apiResult, patientData) {
        const report = this.elements.treatmentReport;
        if (!report) return;
        
        const severity = apiResult.severity || 'moderate';
        const urgency = apiResult.urgency || 'routine';
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-prescription"></i> Evidence-Based Treatment Plan</h3>
                <span class="report-timestamp">Guideline-based • ${new Date().toLocaleDateString()}</span>
                <div class="api-badge">
                    ${apiResult.source && apiResult.source.includes('Gemini') ? 
                        '<i class="fas fa-robot"></i> Gemini AI Enhanced' : 
                        '<i class="fas fa-stethoscope"></i> ML Based'}
                </div>
            </div>
            
            <div class="treatment-plan">
                ${apiResult.treatment_plan && Object.keys(apiResult.treatment_plan).length > 0 ? `
                    <div class="treatment-section">
                        <h4><i class="fas fa-pills"></i> Recommended Interventions</h4>
                        <div class="interventions-list">
                            ${Object.entries(apiResult.treatment_plan).map(([key, value]) => `
                                <div class="intervention-card">
                                    <i class="fas fa-${this.getTreatmentIcon(key)}"></i>
                                    <div>
                                        <strong>${this.formatTreatmentKey(key)}</strong>
                                        <p>${value}</p>
                                        <span class="priority ${severity === 'critical' ? 'high' : severity === 'severe' ? 'medium' : 'standard'}">
                                            ${severity === 'critical' ? 'HIGH PRIORITY' : 
                                              severity === 'severe' ? 'MEDIUM PRIORITY' : 'STANDARD PRIORITY'}
                                        </span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <div class="no-treatment-plan">
                        <i class="fas fa-info-circle"></i>
                        <h4>Standard Care Recommended</h4>
                        <p>Follow-up with healthcare provider for evaluation and management based on diagnosis.</p>
                    </div>
                `}
                
                <div class="treatment-section">
                    <h4><i class="fas fa-exclamation-triangle"></i> Urgency & Follow-up</h4>
                    <div class="urgency-card ${urgency}">
                        <div class="urgency-header">
                            <i class="fas fa-${urgency === 'emergency' ? 'ambulance' : 
                                             urgency === 'urgent' ? 'exclamation-triangle' : 
                                             'calendar-check'}"></i>
                            <div>
                                <strong>${urgency.toUpperCase()} CARE</strong>
                                <p>Recommended timeline for follow-up</p>
                            </div>
                        </div>
                        <div class="urgency-content">
                            <p>Based on the ${severity} severity assessment, ${urgency} care is recommended.</p>
                            ${urgency === 'emergency' ? 
                                '<p><strong>Immediate medical attention required.</strong> Proceed to emergency department.</p>' :
                              urgency === 'urgent' ? 
                                '<p><strong>Seek medical care within 24 hours.</strong> Contact primary care provider.</p>' :
                                '<p><strong>Routine follow-up recommended.</strong> Schedule appointment within 1-2 weeks.</p>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        report.classList.add('active');
    }

    generatePatientSummaryFromAPI(apiResult, patientData) {
        const report = this.elements.patientReport;
        if (!report) return;
        
        const severity = apiResult.severity || 'moderate';
        const confidence = apiResult.confidence || 'medium';
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-user-circle"></i> Patient Summary</h3>
                <span class="report-timestamp">Complete profile • ${new Date().toLocaleDateString()}</span>
                <div class="api-badge">
                    <i class="fas fa-robot"></i> AI Enhanced Summary
                </div>
            </div>
            
            <div class="patient-summary-content">
                <div class="summary-grid">
                    <div class="summary-section">
                        <h4><i class="fas fa-user-injured"></i> Patient Profile</h4>
                        <div class="profile-details">
                            <div class="detail-item">
                                <span>Age:</span>
                                <strong>${patientData.age} years</strong>
                            </div>
                            <div class="detail-item">
                                <span>Gender:</span>
                                <strong>${patientData.gender}</strong>
                            </div>
                            <div class="detail-item">
                                <span>Pain Score:</span>
                                <strong>${patientData.painScore}/10</strong>
                            </div>
                        </div>
                    </div>
                    
                    <div class="summary-section">
                        <h4><i class="fas fa-stethoscope"></i> Clinical Findings</h4>
                        <div class="findings-details">
                            <div class="detail-item">
                                <span>Diagnosis:</span>
                                <strong>${apiResult.primary_diagnosis}</strong>
                            </div>
                            <div class="detail-item">
                                <span>Severity:</span>
                                <strong class="severity-${severity}">${severity}</strong>
                            </div>
                            <div class="detail-item">
                                <span>Confidence:</span>
                                <strong>${confidence}</strong>
                            </div>
                        </div>
                    </div>
                    
                    <div class="summary-section full-width">
                        <h4><i class="fas fa-comment-medical"></i> Clinical Reasoning</h4>
                        <div class="reasoning-text">
                            <p>${apiResult.reasoning}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        report.classList.add('active');
    }

    generateRiskAnalysisFromAPI(apiResult, patientData) {
        const report = this.elements.riskReport;
        if (!report) return;
        
        const severity = apiResult.severity || 'moderate';
        const urgency = apiResult.urgency || 'routine';
        const severityScore = apiResult.severity_score || 5;
        
        let riskLevel = 'low';
        let riskColor = 'success';
        if (severity === 'critical' || urgency === 'emergency') {
            riskLevel = 'critical';
            riskColor = 'danger';
        } else if (severity === 'severe' || urgency === 'urgent') {
            riskLevel = 'high';
            riskColor = 'warning';
        } else if (severity === 'moderate') {
            riskLevel = 'moderate';
            riskColor = 'warning';
        }
        
        report.innerHTML = `
            <div class="report-header">
                <h3><i class="fas fa-exclamation-triangle"></i> Risk Analysis</h3>
                <span class="report-timestamp">Comprehensive assessment • ${new Date().toLocaleDateString()}</span>
                <div class="api-badge">
                    <i class="fas fa-chart-line"></i> AI Risk Assessment
                </div>
            </div>
            
            <div class="risk-analysis-content">
                <div class="risk-assessment">
                    <div class="risk-score-display">
                        <div class="risk-meter">
                            <div class="meter-fill ${riskColor}" style="width: ${(severityScore / 10) * 100}%"></div>
                        </div>
                        <div class="risk-value">
                            <strong>Risk Score: ${severityScore}/10</strong>
                            <span class="risk-level ${riskLevel}">${riskLevel.toUpperCase()} RISK</span>
                        </div>
                    </div>
                    
                    <div class="risk-factors">
                        <h4><i class="fas fa-list-check"></i> Key Risk Factors</h4>
                        <ul>
                            <li><strong>Clinical Severity:</strong> ${severity}</li>
                            <li><strong>Urgency Level:</strong> ${urgency}</li>
                            <li><strong>Pain Score:</strong> ${patientData.painScore}/10</li>
                            <li><strong>Age Factor:</strong> ${patientData.age < 2 || patientData.age > 65 ? 'High risk age group' : 'Standard risk age group'}</li>
                        </ul>
                    </div>
                    
                    <div class="recommendations">
                        <h4><i class="fas fa-lightbulb"></i> Risk Mitigation</h4>
                        <div class="recommendation-card ${riskColor}">
                            <i class="fas fa-${riskLevel === 'critical' ? 'ambulance' : 'shield-alt'}"></i>
                            <div>
                                <strong>${riskLevel === 'critical' ? 'Emergency Response Required' : 
                                         riskLevel === 'high' ? 'Urgent Medical Attention Needed' : 
                                         'Standard Monitoring Recommended'}</strong>
                                <p>${riskLevel === 'critical' ? 'Immediate intervention required. Proceed to emergency care.' :
                                   riskLevel === 'high' ? 'Seek medical attention within 24 hours. Monitor symptoms closely.' :
                                   'Follow-up with healthcare provider as scheduled. Monitor for any changes in condition.'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        report.classList.add('active');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) {
            console.warn('Toast container not found');
            return;
        }
        
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
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
        
        toast.querySelector('.close-toast').addEventListener('click', () => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        });
    }
}

class MediPatientAPIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.endpoints = {
            predict: '/api/predict',
            status: '/api/status',
            getReports: '/api/get-reports'
        };
    }

    async checkAPIStatus() {
        try {
            const response = await fetch(this.endpoints.status);
            return await response.json();
        } catch (error) {
            console.error('API Status Check Failed:', error);
            return { status: 'offline', error: error.message };
        }
    }

    async predict(patientData) {
        try {
            console.log('Sending prediction request to API:', patientData);
            
            const response = await fetch(this.endpoints.predict, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(patientData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Prediction response received:', result);
            return result;

        } catch (error) {
            console.error('Prediction API Error:', error);
            throw error;
        }
    }

    async getReports() {
        try {
            const response = await fetch(this.endpoints.getReports);
            return await response.json();
        } catch (error) {
            console.error('Get Reports API Error:', error);
            throw error;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.mediPatientAI = new MediPatientAI();
});