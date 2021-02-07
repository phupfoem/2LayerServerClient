const mongoose = require('mongoose');
const Schema = mongoose.Schema;

let LogSchema = new Schema({
    data: { type: Number, required: true },
});

// Export the model
module.exports = mongoose.model('Log', LogSchema);