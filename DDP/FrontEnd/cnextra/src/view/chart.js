import React from 'react';

import { Line } from 'react-chartjs-2';


const Chart = ({ datareceived, ...rest }) => {
    console.log(datareceived)
    const data = {
        labels: datareceived.label,
        datasets: [
            {
                data: datareceived.data,
                label: "Step",
                borderColor: "#3e95cd",
                fill: false
            }
        ]
    }

    const options = {
        title: {
            display: true,
            text: "Loss value"
        },
        legend: {
            display: true,
            position: "bottom"
        }
    }
    return (
        <div>
            <Line
                data={data}
                options={options}
            />
        </div>
    );
};

export default Chart;
