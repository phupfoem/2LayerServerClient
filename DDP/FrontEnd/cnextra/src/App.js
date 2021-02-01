import logo from './logo.svg';
import './App.css';
import firebase from './database/firebase'
import React, { useState, useEffect } from 'react'
import Chart from './view/chart'
import axios from 'axios';

const App = () => {
    const db = firebase.database();
    const [data, setData] = useState({ data: [], label: [] })

    // useEffect(() => {
    //     const dataRef = firebase.database().ref('lossdata');
    //     dataRef.on('value', (snapshot) => {
    //         const dataReceived = snapshot.val();
    //         const newdata = { data: [], label: [] }
    //         let j = 0
    //         console.log("change")
    //         console.log(dataReceived)
    //         for (let id in dataReceived) {
    //             if (dataReceived[id].length > 0) {
    //                 newdata.data = newdata.data.concat(dataReceived[id])
    //                 for (let i = 0; i < dataReceived[id].length; i++)
    //                     newdata.label.push(j++)
    //             }
    //             // newdata.data.push(dataReceived[id])
    //             // newdata.label.push(j++)
    //         }
    //         setData(newdata)
    //     });
    // }, [])
    let id = null
    useEffect(() => {
        const getdata = async () => {
            try {
                const config = {
                    method: 'get',
                    url: "http://localhost:9000/log",
                };
                await axios(config).then(respose => {
                    console.log(respose.data.data[0])
                    const newdata = { data: [], label: [] }
                    const datareceived = respose.data.data
                    for (let i = 0; i < respose.data.data.length; i++) {
                        newdata.label.push(i + 1)
                        newdata.data.push(datareceived[i].data)
                    }
                    if (newdata.data.length === data.data.length) clearInterval(id);
                    setData(newdata)
                })
            }
            catch (er) {
                console.log(er)
            }
        }
        id = setInterval(getdata, 1000);
        return () => clearInterval(id);
    }, []);
    return (
        <div className="App">
            <Chart datareceived={data} />
        </div>
    );
}

export default App;
