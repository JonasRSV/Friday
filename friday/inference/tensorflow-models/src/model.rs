use tensorflow_rust_sys;
use std::path::Path;
use std::ffi::CString;
use libc;

fn is_status_ok(status: *const tensorflow_rust_sys::TF_Status) -> bool {
    unsafe {
        if tensorflow_rust_sys::TF_GetCode(status) != tensorflow_rust_sys::TF_Code_TF_OK {
            let message = CString::from_raw(tensorflow_rust_sys::TF_Message(status) as *mut i8);
            let rust_message = message.to_str().expect("Failed to make string");

            eprintln!("(tensorflow-models): Error {}", rust_message);

            return false;
        }

        return true;
    }
}

pub struct Tensor {
    tensor: *mut tensorflow_rust_sys::TF_Tensor,
    op: tensorflow_rust_sys::TF_Output,

    pub dims: Vec<i64>,

    data_type: tensorflow_rust_sys::TF_DataType,
    data: *mut libc::c_void,

    is_empty: bool,
    is_valid: bool

}

impl Tensor {
    pub fn new(model: &Model, op_name: &CString) -> Tensor {
        println!("Loading tensor {}", op_name.to_str().expect("Failed to convert op_name to string"));
        let op = tensorflow_rust_sys::TF_Output {
            oper: unsafe { tensorflow_rust_sys::TF_GraphOperationByName(model.graph, op_name.as_ptr()) },
            index:  0
        };

        if op.oper.is_null() {
            panic!("(tensorflow-models): No operation named {}", 
                op_name.to_str().expect("Failed to convert op_name to string"));
        }


        // Get number of dimensions
        let n_dims = unsafe { tensorflow_rust_sys::TF_GraphGetTensorNumDims(model.graph, op, model.status) };
        if !is_status_ok(model.status) {
            panic!("(tensorflow-models): Failed to get dims of op {}", op_name.to_str().expect("Failed to convert op_name to string"))
        }

        let data_type = unsafe { tensorflow_rust_sys::TF_OperationOutputType(op) };

        if n_dims != 1 {
            panic!("(tensorflow-models): Only vector tensors are currently supported");
        }

        let mut dims: Vec<i64> = Vec::new();
        let c_dims = unsafe {libc::malloc(std::mem::size_of::<i64>() * n_dims as usize) as *mut i64};

        unsafe { tensorflow_rust_sys::TF_GraphGetTensorShape(model.graph, op, c_dims, n_dims, model.status) };

        if ! is_status_ok(model.status) {
            panic!("(tensorflow-models): Failed to get shape of tensor for op {}", 
                op_name.to_str().expect("Failed to convert op_name to string"))
        }

        for i in 0..n_dims {
            dims.push(unsafe { *c_dims.add(i as usize)  });
        }

        println!("Successfully loaded Tensor");
        return Tensor{
            tensor: std::ptr::null::<tensorflow_rust_sys::TF_Tensor>() as *mut tensorflow_rust_sys::TF_Tensor,
            op,
            dims,
            data_type,
            data: std::ptr::null::<libc::c_void>() as *mut libc::c_void,
            is_empty: true,
            is_valid: true

        };
    }

    pub fn set_data(&mut self, data: &Vec<i16>) {
        if !self.is_empty {
            unsafe {tensorflow_rust_sys::TF_DeleteTensor(self.tensor) };
            self.is_empty = true
        }

        if !self.is_valid {
            panic!("(tensorflow-models): Trying to set data on an invalid tensor");
        }


        let data_sz = std::mem::size_of::<i16>() * data.len();

        let c_data = unsafe {libc::malloc(data_sz)};
        unsafe { libc::memcpy(c_data, data.as_ptr() as *const libc::c_void, data_sz) };

        unsafe extern "C" fn deallocator(
            data: *mut libc::c_void,
            _: tensorflow_rust_sys::size_t,
            _: *mut libc::c_void,
        ) {
            libc::free(data);
        }

        self.tensor = unsafe {
            tensorflow_rust_sys::TF_NewTensor(
                /*TF_DataType=*/self.data_type, 
                /*dims=*/self.dims.as_ptr(), 
                /*num_dims=*/self.dims.len() as i32, 
                /*data=*/c_data, 
                /*length=*/data_sz as u64,
                /*deallocator=*/Some(deallocator),
                /*deallocator_args=*/std::ptr::null::<libc::c_void>() as *mut libc::c_void)
        };

        if self.tensor.is_null() {
            panic!("(tensorflow-models): Failed to allocate new tensor when setting data");
        }

        self.is_empty = false;
    }

    pub fn get_data<T>(&mut self) -> Vec<T> 
        where T: Clone {
            if self.is_empty {
                panic!("(tensorflow-models): Trying to get data from empty tensor");
            }

            if !self.is_valid {
                panic!("(tensorflow-models): Trying to get data from an invalid tensor");
            }

            let data = unsafe {
                tensorflow_rust_sys::TF_TensorData(self.tensor)
            };

            if data.is_null() {
                panic!("(tensorflow-models): Tensor data is empty");
            }

            let data_size = self.dims.first().expect("(tensorflow-models): Failed to unwrap dims").clone() as usize;
            return unsafe { std::slice::from_raw_parts(data as *const T, data_size).to_vec()};
        }

    fn free_tensor(&mut self) {
        if !self.is_empty {
            unsafe {tensorflow_rust_sys::TF_DeleteTensor(self.tensor) };
        }
        self.is_empty = true;
        self.data = std::ptr::null::<libc::c_void>() as *mut libc::c_void;
    }

}

pub struct Model {
    graph: *mut tensorflow_rust_sys::TF_Graph,
    session: *mut tensorflow_rust_sys::TF_Session,
    status: *mut tensorflow_rust_sys::TF_Status
}

impl Model {

    pub fn free_tensorflow_resources(&mut self) -> bool {
        unsafe {
            tensorflow_rust_sys::TF_DeleteGraph(self.graph);
            tensorflow_rust_sys::TF_DeleteSession(self.session, self.status);

            if is_status_ok(self.status) {
                tensorflow_rust_sys::TF_DeleteStatus(self.status);

                return true;
            }
            return false;
        };

    }

    pub fn new(export_dir: &Path) -> Option<Model> {
        println!("(tensorflow-models): Loading {}", export_dir.to_str().expect("Failed to convert path to String"));
        let status = unsafe { tensorflow_rust_sys::TF_NewStatus() };
        let graph = unsafe { tensorflow_rust_sys::TF_NewGraph() };
        let session_options = unsafe { tensorflow_rust_sys::TF_NewSessionOptions() };

        // This is a encoded proto that tells tensorflow to only use one thread in inference (to
        // save resources)
        let magic_string = CString::new("\x10\x01(\x01").expect("Failed to create magic str");
        let magic_void : *mut libc::c_void = magic_string.as_ptr() as *mut libc::c_void;


        unsafe {tensorflow_rust_sys::TF_SetConfig(
            /*options=*/session_options, 
            /*proto=*/magic_void, 
            /*proto_len=*/4, 
            /*status=*/status) 
        };

        if ! is_status_ok(status) {
            return None;
        }


        let null_ptr: *mut tensorflow_rust_sys::TF_Buffer = 
            std::ptr::null::<tensorflow_rust_sys::TF_Buffer>() as *mut tensorflow_rust_sys::TF_Buffer;


        let export_dir: CString = CString::new(export_dir.to_str()
            .expect("Failed to convert path to String"))
            .expect("Failed to create CString");

        let tags = CString::new("serve").expect("Failed to create CString");

        let session = unsafe { tensorflow_rust_sys::TF_LoadSessionFromSavedModel(
            /*session_options=*/session_options,
            /*run_options=*/null_ptr,
            /*export_dir=*/export_dir.as_ptr(),
            /*tags=*/&tags.as_ptr(),
            /*ntags=*/1,
            /*graph=*/graph, 
            null_ptr,
            /*status=*/status)
        };

        // Can delete sess opts here already since we wont use em
        unsafe { tensorflow_rust_sys::TF_DeleteSessionOptions(session_options) };

        if is_status_ok(status) {
            println!("(tensorflow-models): Successfully loaded model");
            return Some(Model {
                graph,
                session,
                status
            });
        }

        return None
    }

    pub fn run(&mut self, input: &mut Tensor, output: &mut Tensor) {
        if input.is_empty {
            panic!("(tensorflow-models): Trying to run with empty input tensor");
        }

        if !output.is_valid {
            panic!("(tensorflow-models): Trying to run with invalid output tensor");
        }


        let null_ptr: *mut tensorflow_rust_sys::TF_Buffer = 
            std::ptr::null::<tensorflow_rust_sys::TF_Buffer>() as *mut tensorflow_rust_sys::TF_Buffer;

        // Clear output
        output.free_tensor();

        unsafe {
            tensorflow_rust_sys::TF_SessionRun(
                /*session=*/self.session,
                /*run_opts=*/null_ptr,
                /*input_ops=*/&input.op,
                /*input_values=*/&input.tensor,
                /*num_inputs=*/1,
                /*output_ops=*/&output.op,
                /*output_values=*/&mut output.tensor,
                /*num_outputs=*/1,
                /*target_operations=*/&(null_ptr as *const tensorflow_rust_sys::TF_Operation),
                /*num_targets=*/0,
                /*run_metadata=*/null_ptr,
                /*status=*/self.status)
        };

        if is_status_ok(self.status) {
            output.is_empty = false;
            input.free_tensor();
        } else {
            panic!("(tensorflow-models): Failed to execute tensorflow session");
        }
    }

}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_load_model_and_tensors() {
        let model_path = Path::new("test-resources/1602921240");
        let mut model = Model::new(&model_path).expect("Failed to create model");

        let input_op_name = CString::new("input").expect("Failed to create input name");
        let output_op_name = CString::new("output").expect("Failed to create output name");

        let mut input_tensor = Tensor::new(&model, &input_op_name);
        let mut output_tensor = Tensor::new(&model, &output_op_name);

        let v: Vec<i16> = vec![1; 16000];

        println!("Tensor size {}", v.len());
        println!("datatype {}", input_tensor.data_type);

        input_tensor.set_data(&v);
        let u: Vec<i16> = input_tensor.get_data();
        assert_eq!(v, u);

        model.run(&mut input_tensor, &mut output_tensor);

        println!("output datatype: {}", output_tensor.data_type);
        println!("{:?}", output_tensor.get_data::<f32>());

        println!("Loading went fine!");
        model.free_tensorflow_resources();

        println!("Freeing went fine Woo!");
    }
}
