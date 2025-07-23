"""
Configuration interface for agent settings.
"""
import gradio as gr

def create_config():
    """Create the configuration interface."""
    with gr.Column():
        gr.Markdown("## Agent Configuration")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Agent Settings")
                
                agent_name = gr.Textbox(
                    label="Agent Name",
                    placeholder="Enter agent name..."
                )
                
                model_name = gr.Dropdown(
                    label="Model",
                    choices=["gpt-4", "gpt-3.5-turbo", "claude-3", "custom"],
                    value="gpt-4"
                )
                
                temperature = gr.Slider(
                    label="Temperature",
                    minimum=0.0,
                    maximum=2.0,
                    value=0.7,
                    step=0.1
                )
                
                max_tokens = gr.Number(
                    label="Max Tokens",
                    value=2048,
                    minimum=1,
                    maximum=8192
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### System Configuration")
                
                system_prompt = gr.Textbox(
                    label="System Prompt",
                    lines=10,
                    placeholder="Enter system prompt..."
                )
                
                tools_enabled = gr.CheckboxGroup(
                    label="Enabled Tools",
                    choices=["web_search", "calculator", "file_operations", "database"],
                    value=["web_search"]
                )
        
        with gr.Row():
            save_config_btn = gr.Button("Save Configuration", variant="primary")
            load_config_btn = gr.Button("Load Configuration")
            reset_config_btn = gr.Button("Reset to Defaults", variant="secondary")
        
        config_status = gr.Textbox(
            label="Status",
            interactive=False,
            value="Ready to configure agent settings"
        )
        
        def save_configuration(name, model, temp, tokens, prompt, tools):
            # Placeholder for saving configuration
            return f"Configuration saved for agent '{name}' with model {model}"
        
        def load_configuration():
            # Placeholder for loading configuration
            return "Default", "gpt-4", 0.7, 2048, "You are a helpful assistant.", ["web_search"]
        
        def reset_configuration():
            # Placeholder for resetting configuration
            return "Default Agent", "gpt-4", 0.7, 2048, "", []
        
        save_config_btn.click(
            fn=save_configuration,
            inputs=[agent_name, model_name, temperature, max_tokens, system_prompt, tools_enabled],
            outputs=[config_status]
        )
        
        load_config_btn.click(
            fn=load_configuration,
            outputs=[agent_name, model_name, temperature, max_tokens, system_prompt, tools_enabled]
        )
        
        reset_config_btn.click(
            fn=reset_configuration,
            outputs=[agent_name, model_name, temperature, max_tokens, system_prompt, tools_enabled]
        )