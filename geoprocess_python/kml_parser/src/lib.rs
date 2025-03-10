use pyo3::prelude::*;
use quick_xml::Reader;
use quick_xml::events::Event;
use std::fs::File;
use std::io::BufReader;
use std::collections::HashMap;

#[pyfunction]
fn parse_kml(filepath: &str) -> PyResult<Vec<HashMap<String, String>>> {
    let file = File::open(filepath).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Error opening file: {}", e)))?;
    let reader = BufReader::new(file);
    let mut xml_reader = Reader::from_reader(reader);

    let mut buf = Vec::new();
    let mut schemas = Vec::new();
    let mut current_schema = HashMap::new();

    loop {
        match xml_reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) if e.name().as_ref() == b"SimpleData" => {
                if let Some(attr) = e.attributes().flatten().find(|a| a.key.as_ref() == b"name") {
                    let name = String::from_utf8_lossy(&attr.value).to_string();
                    current_schema.insert(name, String::new());
                }
            }
            Ok(Event::Text(e)) => {
                // Extract the last key from the HashMap
                let key = current_schema.keys().last().cloned();
                if let Some(key) = key {
                    let text = e.unescape().map_err(|e| {
                        PyErr::new::<pyo3::exceptions::PyUnicodeDecodeError, _>(format!("Error decoding text: {}", e))
                    })?;
                    // Update the value for the extracted key
                    current_schema.insert(key, text.into_owned());
                }
            }
            Ok(Event::End(ref e)) if e.name().as_ref() == b"SchemaData" => {
                schemas.push(current_schema.clone());
                current_schema.clear();
            }
            Ok(Event::Eof) => break,
            Err(e) => return Err(PyErr::new::<pyo3::exceptions::PyException, _>(format!("XML parsing error: {}", e))),
            _ => (),
        }
        buf.clear();
    }

    Ok(schemas)
}

#[pymodule]
fn kml_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_kml, m)?)?;
    Ok(())
}