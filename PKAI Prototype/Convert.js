const {
  convertAll
} = require('bpmn-to-image');

convertAll([
  {
    input: 'Outputs/sketch.bpmn',
    outputs: [
      "Outputs/diagram.png"
    ]
  }
]);