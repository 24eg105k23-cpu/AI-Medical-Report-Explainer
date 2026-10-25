export const MOCK_REPORTS = [
  {
    id: 'r1',
    name: 'Complete Blood Count',
    date: '26 August 2026',
    parameters: 14,
    status: 'normal',
    type: 'Blood Test'
  },
  {
    id: 'r2',
    name: 'Lipid Profile',
    date: '10 July 2026',
    parameters: 5,
    status: 'attention',
    type: 'Blood Test'
  },
  {
    id: 'r3',
    name: 'Liver Function Test',
    date: '15 March 2026',
    parameters: 8,
    status: 'normal',
    type: 'Blood Test'
  }
];

export const MOCK_REPORT_DETAILS = {
  r1: {
    name: 'Complete Blood Count',
    date: '26 August 2026',
    summary: 'Most of the values in this report are within the expected range. A few values may require discussion with your doctor.',
    statusSummary: 'Mostly within expected range',
    stats: {
      normal: 12,
      high: 1,
      low: 1
    },
    parameters: [
      { id: 'p1', name: 'Hemoglobin', value: '14.5', unit: 'g/dL', range: '13.8 - 17.2 g/dL', status: 'normal', explanation: 'A protein in red blood cells that carries oxygen.', termMeaning: 'It helps carry oxygen throughout your body.' },
      { id: 'p2', name: 'RBC', value: '4.8', unit: 'million/mcL', range: '4.5 - 5.9 million/mcL', status: 'normal', explanation: 'Red blood cells carry oxygen.', termMeaning: 'The cells that carry oxygen.' },
      { id: 'p3', name: 'WBC', value: '11.5', unit: 'thousand/mcL', range: '4.5 - 11.0 thousand/mcL', status: 'high', explanation: 'White blood cells fight infection. A slightly high value might indicate a minor infection.', termMeaning: 'Cells of the immune system involved in protecting the body.' },
      { id: 'p4', name: 'Platelets', value: '140', unit: 'thousand/mcL', range: '150 - 450 thousand/mcL', status: 'low', explanation: 'Platelets help blood clot. A slightly low value should be monitored.', termMeaning: 'Cell fragments that form clots and stop or prevent bleeding.' }
    ],
    questions: [
      'What does my slightly high WBC count indicate?',
      'Should I be concerned about the lower platelet count?',
      'Do I need any additional tests or follow-ups?'
    ]
  },
  r2: {
    name: 'Lipid Profile',
    date: '10 July 2026',
    summary: 'Some cholesterol values are above the recommended range. Lifestyle changes may be suggested by your doctor.',
    statusSummary: 'Needs Attention',
    stats: {
      normal: 3,
      high: 2,
      low: 0
    },
    parameters: [
      { id: 'p5', name: 'Total Cholesterol', value: '240', unit: 'mg/dL', range: 'Below 200 mg/dL', status: 'high', explanation: 'Overall cholesterol level in your blood.', termMeaning: 'A waxy substance found in your blood.' },
      { id: 'p6', name: 'LDL Cholesterol', value: '190', unit: 'mg/dL', range: 'Below 100 mg/dL', status: 'high', explanation: 'Your LDL cholesterol is above the displayed reference range. Discuss this result with your healthcare professional.', termMeaning: 'Often called "bad" cholesterol.' },
      { id: 'p7', name: 'HDL Cholesterol', value: '45', unit: 'mg/dL', range: 'Above 40 mg/dL', status: 'normal', explanation: 'Good cholesterol that helps remove other forms of cholesterol.', termMeaning: 'Often called "good" cholesterol.' },
      { id: 'p8', name: 'Triglycerides', value: '140', unit: 'mg/dL', range: 'Below 150 mg/dL', status: 'normal', explanation: 'A type of fat found in your blood.', termMeaning: 'The most common type of fat in your body.' }
    ],
    questions: [
      'What does this high LDL value mean for me?',
      'Are there lifestyle changes I should consider?',
      'Could this result be affected by my diet?'
    ]
  }
};

export const MOCK_MEDICINES = [
  {
    id: 'm1',
    name: 'Paracetamol',
    strength: '500 mg',
    form: 'Tablet',
    manufacturer: 'HealthPharm Inc.',
    price: 45.00,
    availability: 'In Stock',
    prescriptionRequired: false,
    description: 'Used to treat mild to moderate pain and reduce fever.',
    image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'
  },
  {
    id: 'm2',
    name: 'Atorvastatin',
    strength: '10 mg',
    form: 'Tablet',
    manufacturer: 'CardioCare Ltd.',
    price: 120.00,
    availability: 'In Stock',
    prescriptionRequired: true,
    description: 'Used to lower cholesterol levels in the blood.',
    image: 'https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'
  },
  {
    id: 'm3',
    name: 'Amoxicillin',
    strength: '250 mg',
    form: 'Capsule',
    manufacturer: 'BioMed Corp.',
    price: 85.00,
    availability: 'Low Stock',
    prescriptionRequired: true,
    description: 'An antibiotic used to treat various bacterial infections.',
    image: 'https://images.unsplash.com/photo-1576086213369-97a306d36557?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'
  }
];

export const MOCK_EXTRACTED_PRESCRIPTION = [
  {
    id: 'e1',
    medicineName: 'Paracetamol',
    strength: '500 mg',
    dosage: '1 tablet',
    frequency: 'After food',
    duration: '3 days',
    instructions: 'Take when fever is high.',
    status: 'verified',
    matchedMedicine: MOCK_MEDICINES[0]
  },
  {
    id: 'e2',
    medicineName: 'Azithromycin',
    strength: '500 mg',
    dosage: '1 tablet',
    frequency: 'Once a day',
    duration: '5 days',
    instructions: 'Complete the full course.',
    status: 'needs_review',
    matchedMedicine: null
  }
];
