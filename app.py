import argparse
import gradio as gr
from gradio_i18n import Translate, gettext as _

from modules.live_portrait.live_portrait_inferencer import LivePortraitInferencer
from modules.utils.paths import *
from modules.utils.helper import str2bool
from modules.utils.constants import *
import os

class App:
    def __init__(self, args=None):
        self.args = args
        self.app = gr.Blocks(css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: 0 auto !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: #f0f2f6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 1.5rem;
            }
            .header {
                text-align: center;
                padding: 2rem 0;
                color: #1a1a1a;
            }
            .header h1 {
                font-size: 2.8rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: #1a1a1a;
            }
            .header p {
                font-size: 1.2rem;
                color: #4a4a4a;
            }
            .card {
                border-radius: 12px;
                background: #ffffff;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                margin-bottom: 1.5rem;
                border: 1px solid #e5e7eb;
            }
            .card-header {
                background: #f8fafc;
                padding: 1rem;
                border-bottom: 1px solid #e5e7eb;
                font-weight: 600;
                color: #1e293b;
                font-size: 1.25rem;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            .card-body {
                padding: 1.5rem;
                background: #ffffff;
            }
            .btn-primary {
                background: linear-gradient(90deg, #3b82f6 0%, #7c3aed 100%);
                border: none;
                color: #ffffff;
                padding: 0.75rem 2rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-primary:hover {
                opacity: 0.9;
                transform: translateY(-2px);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .btn-secondary {
                background: #6b7280;
                color: #ffffff;
                padding: 0.75rem 2rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-secondary:hover {
                background: #4b5563;
            }
            .btn-reset {
                background: #ef4444;
                color: #ffffff;
                padding: 0.75rem 2rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-reset:hover {
                background: #dc2626;
            }
            .preset-btn {
                margin: 0.3rem;
                padding: 0.6rem 1.2rem;
                border-radius: 20px;
                border: 1px solid #d1d5db;
                background: #ffffff;
                color: #374151;
                cursor: pointer;
                transition: all 0.2s;
                font-weight: 500;
            }
            .preset-btn:hover {
                background: #f3f4f6;
                transform: scale(1.03);
            }
            .preset-btn.active {
                background: #3b82f6;
                color: #ffffff;
                border-color: #3b82f6;
            }
            .tab-nav {
                border-bottom: 2px solid #e5e7eb;
                margin-bottom: 1.5rem;
                display: flex;
            }
            .tab-btn {
                padding: 1rem 2rem;
                background: none;
                border: none;
                border-bottom: 2px solid transparent;
                margin-bottom: -2px;
                cursor: pointer;
                font-weight: 600;
                color: #1e293b;
                font-size: 1.1rem;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                transition: all 0.2s;
            }
            .tab-btn.active {
                border-bottom: 2px solid #3b82f6;
                color: #3b82f6;
            }
            .footer {
                text-align: center;
                padding: 2rem;
                color: #6b7280;
                font-size: 1rem;
            }
            .gr-slider label, .gr-checkbox label {
                color: #2d3748 !important;
                font-weight: 500;
            }
            .gr-slider span, .gr-checkbox span {
                color: #4b5563 !important;
            }
            h3 {
                color: #1e293b !important;
                font-weight: 600 !important;
                font-size: 1.2rem !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            }
        """)
        self.i18n = Translate(I18N_YAML_PATH)
        self.inferencer = LivePortraitInferencer(
            model_dir=args.model_dir if args else MODELS_DIR,
            output_dir=args.output_dir if args else OUTPUTS_DIR
        )
        
        self.expression_presets = {
            "Neutral": {
                "rotate_pitch": 0, "rotate_yaw": 0, "rotate_roll": 0,
                "blink": 0, "eyebrow": 0, "wink": 0,
                "pupil_x": 0, "pupil_y": 0,
                "aaa": 0, "eee": 0, "woo": 0,
                "smile": 0, "source_ratio": 1
            },
            "Happy": {
                "rotate_pitch": -2, "rotate_yaw": 0, "rotate_roll": 0,
                "blink": -3, "eyebrow": 10, "wink": 0,
                "pupil_x": 0, "pupil_y": 3,
                "aaa": 15, "eee": 10, "woo": 0,
                "smile": 1.2, "source_ratio": 0.95
            },
            "Sad": {
                "rotate_pitch": 4, "rotate_yaw": 0, "rotate_roll": 0,
                "blink": 3, "eyebrow": -20, "wink": 0,
                "pupil_x": 0, "pupil_y": -4,
                "aaa": 5, "eee": -5, "woo": 5,
                "smile": -1.0, "source_ratio": 0.95
            },
            "Angry": {
                "rotate_pitch": -3, "rotate_yaw": 0, "rotate_roll": 0,
                "blink": 2, "eyebrow": -25, "wink": 0,
                "pupil_x": 0, "pupil_y": -2,
                "aaa": 10, "eee": -10, "woo": 0,
                "smile": -0.5, "source_ratio": 0.95
            },
            "Sleepy": {
                "rotate_pitch": 3, "rotate_yaw": 0, "rotate_roll": 0,
                "blink": -5, "eyebrow": 15, "wink": 0,
                "pupil_x": 0, "pupil_y": 4,
                "aaa": 40, "eee": 0, "woo": 0,
                "smile": 0, "source_ratio": 0.95
            },
            "Winking": {
                "rotate_pitch": 0, "rotate_yaw": 2, "rotate_roll": 0,
                "blink": 0, "eyebrow": 8, "wink": 15,
                "pupil_x": 4, "pupil_y": 0,
                "aaa": 0, "eee": 5, "woo": 0,
                "smile": 0.8, "source_ratio": 0.95
            },
            "Thinking": {
                "rotate_pitch": 2, "rotate_yaw": 4, "rotate_roll": 0,
                "blink": 1, "eyebrow": 10, "wink": 0,
                "pupil_x": 6, "pupil_y": -3,
                "aaa": 0, "eee": 0, "woo": 3,
                "smile": -0.2, "source_ratio": 0.95
            },
            "Surprised": {
                "rotate_pitch": 3, "rotate_yaw": 0, "rotate_roll": 0,
                "blink": 5, "eyebrow": -10, "wink": 0,
                "pupil_x": 0, "pupil_y": 2,
                "aaa": 5, "eee": 0, "woo": 5,
                "smile": -0.3, "source_ratio": 0.95
            }
        }

    def apply_preset(self, preset_name, model_type, pitch, yaw, roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, source_ratio, sample_ratio, sample_parts, face_crop, restoration, ref_image):
        if preset_name not in self.expression_presets:
            return [model_type, pitch, yaw, roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, source_ratio, sample_ratio, sample_parts, face_crop, restoration, ref_image]
        
        preset = self.expression_presets[preset_name]
        return [
            model_type, preset["rotate_pitch"], preset["rotate_yaw"], preset["rotate_roll"],
            preset["blink"], preset["eyebrow"], preset["wink"], preset["pupil_x"], preset["pupil_y"],
            preset["aaa"], preset["eee"], preset["woo"], preset["smile"], preset["source_ratio"],
            sample_ratio, sample_parts, face_crop, restoration, ref_image
        ]

    def reset_to_default(self, model_type, pitch, yaw, roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, source_ratio, sample_ratio, sample_parts, face_crop, restoration, ref_image):
        """Reset all settings to default (Neutral) values."""
        return [
            model_type, 0, 0, 0,  # pitch, yaw, roll
            0, 0, 0,  # blink, eyebrow, wink
            0, 0,  # pupil_x, pupil_y
            0, 0, 0,  # aaa, eee, woo
            0, 1,  # smile, source_ratio
            sample_ratio, sample_parts, face_crop, restoration, ref_image
        ]

    def launch(self):
        with self.app:
            with self.i18n:
                with gr.Column(elem_classes="header"):
                    gr.Markdown("# Custom Emotion Generator")
                    gr.Markdown(_("Create expressive face animations from a single image"))

                with gr.Tabs(elem_classes="main-tabs"):
                    with gr.TabItem(_("Expression Editor"), elem_classes="main-tab"):
                        with gr.Row():
                            with gr.Column(scale=2):
                                with gr.Column(elem_classes="card"):
                                    with gr.Row(elem_classes="card-header"):
                                        gr.Markdown(_("Reference Image"))
                                    with gr.Row(elem_classes="card-body"):
                                        img_ref = gr.Image(label=None, elem_classes="ref-image")
                            
                            with gr.Column(scale=3):
                                with gr.Column(elem_classes="card"):
                                    with gr.Row(elem_classes="card-header"):
                                        gr.Markdown(_("Output Preview"))
                                    with gr.Row(elem_classes="card-body"):
                                        img_out = gr.Image(label=None, elem_classes="output-image")
                                        
                        with gr.Column(elem_classes="card"):
                            with gr.Row(elem_classes="card-header"):
                                gr.Markdown(_("Quick Expression Presets"))
                            with gr.Row(elem_classes="card-body"):
                                preset_buttons = []
                                for preset_name in self.expression_presets.keys():
                                    preset_btn = gr.Button(preset_name, elem_classes="preset-btn")
                                    preset_buttons.append(preset_btn)
                        
                        with gr.Column(elem_classes="card"):
                            with gr.Row(elem_classes="card-header"):
                                gr.Markdown(_("Expression Controls"))
                            
                            with gr.Tabs(elem_classes="controls-tabs"):
                                with gr.TabItem(_("Basic"), elem_classes="controls-tab"):
                                    with gr.Row():
                                        with gr.Column():
                                            gr.Markdown("### " + _("Face Rotation"))
                                            pitch_basic = gr.Slider(label=_("Rotate Pitch"), minimum=-20, maximum=20, step=0.5, value=0)
                                            yaw_basic = gr.Slider(label=_("Rotate Yaw"), minimum=-20, maximum=20, step=0.5, value=0)
                                            roll_basic = gr.Slider(label=_("Rotate Roll"), minimum=-20, maximum=20, step=0.5, value=0)
                                        
                                        with gr.Column():
                                            gr.Markdown("### " + _("Eyes"))
                                            blink_basic = gr.Slider(label=_("Blink"), info=_("Value above 5 may appear distorted"), minimum=-20, maximum=20, step=0.5, value=0)
                                            eyebrow_basic = gr.Slider(label=_("Eyebrow"), minimum=-40, maximum=20, step=0.5, value=0)
                                            wink_basic = gr.Slider(label=_("Wink"), minimum=0, maximum=25, step=0.5, value=0)
                                            
                                        with gr.Column():
                                            gr.Markdown("### " + _("Mouth"))
                                            aaa_basic = gr.Slider(label=_("AAA"), minimum=-30, maximum=120, step=1, value=0)
                                            eee_basic = gr.Slider(label=_("EEE"), minimum=-20, maximum=20, step=0.2, value=0)
                                            woo_basic = gr.Slider(label=_("WOO"), minimum=-20, maximum=20, step=0.2, value=0)
                                            smile_basic = gr.Slider(label=_("Smile"), minimum=-2.0, maximum=2.0, step=0.01, value=0)
                                
                                with gr.TabItem(_("Advanced"), elem_classes="controls-tab"):
                                    with gr.Row():
                                        with gr.Column():
                                            gr.Markdown("### " + _("Pupils"))
                                            pupil_x_adv = gr.Slider(label=_("Pupil X"), minimum=-20, maximum=20, step=0.5, value=0)
                                            pupil_y_adv = gr.Slider(label=_("Pupil Y"), minimum=-20, maximum=20, step=0.5, value=0)
                                        
                                        with gr.Column():
                                            gr.Markdown("### " + _("Technical Parameters"))
                                            source_ratio_adv = gr.Slider(label=_("Source Ratio"), minimum=0, maximum=1, step=0.01, value=1)
                                            face_crop_adv = gr.Slider(label=_("Face Crop Factor"), minimum=1.5, maximum=2.5, step=0.1, value=2)
                                            restoration_adv = gr.Checkbox(label=_("Enable Image Restoration"), info=_("This enables image restoration with RealESRGAN but slows down the speed"), value=False)
                                
                                with gr.TabItem(_("All Controls"), elem_classes="controls-tab"):
                                    model_type = gr.Dropdown(label=_("Model Type"), visible=False, interactive=False,
                                                           choices=[item.value for item in ModelType], value=ModelType.HUMAN.value)
                                    pitch = gr.Slider(label=_("Rotate Pitch"), minimum=-20, maximum=20, step=0.5, value=0)
                                    yaw = gr.Slider(label=_("Rotate Yaw"), minimum=-20, maximum=20, step=0.5, value=0)
                                    roll = gr.Slider(label=_("Rotate Roll"), minimum=-20, maximum=20, step=0.5, value=0)
                                    blink = gr.Slider(label=_("Blink"), info=_("Value above 5 may appear distorted"), minimum=-20, maximum=20, step=0.5, value=0)
                                    eyebrow = gr.Slider(label=_("Eyebrow"), minimum=-40, maximum=20, step=0.5, value=0)
                                    wink = gr.Slider(label=_("Wink"), minimum=0, maximum=25, step=0.5, value=0)
                                    pupil_x = gr.Slider(label=_("Pupil X"), minimum=-20, maximum=20, step=0.5, value=0)
                                    pupil_y = gr.Slider(label=_("Pupil Y"), minimum=-20, maximum=20, step=0.5, value=0)
                                    aaa = gr.Slider(label=_("AAA"), minimum=-30, maximum=120, step=1, value=0)
                                    eee = gr.Slider(label=_("EEE"), minimum=-20, maximum=20, step=0.2, value=0)
                                    woo = gr.Slider(label=_("WOO"), minimum=-20, maximum=20, step=0.2, value=0)
                                    smile = gr.Slider(label=_("Smile"), minimum=-2.0, maximum=2.0, step=0.01, value=0)
                                    source_ratio = gr.Slider(label=_("Source Ratio"), minimum=0, maximum=1, step=0.01, value=1)
                                    sample_ratio = gr.Slider(label=_("Sample Ratio"), minimum=-0.2, maximum=1.2, step=0.01, value=1, visible=False)
                                    sample_parts = gr.Dropdown(label=_("Sample Parts"), visible=False,
                                                             choices=[part.value for part in SamplePart], value=SamplePart.ALL.value)
                                    face_crop = gr.Slider(label=_("Face Crop Factor"), minimum=1.5, maximum=2.5, step=0.1, value=2)
                                    restoration = gr.Checkbox(label=_("Enable Image Restoration"),
                                                            info=_("This enables image restoration with RealESRGAN but slows down the speed"), value=False)
                        
                        # Updated button row with Reset button
                        with gr.Row():
                            btn_gen = gr.Button(_("GENERATE"), elem_classes="btn-primary")
                            btn_reset = gr.Button(_("RESET"), elem_classes="btn-reset")
                            btn_openfolder = gr.Button('📂 ' + _("Open Output Folder"), elem_classes="btn-secondary")
                            
                        with gr.Accordion("Opt in features", visible=False):
                            img_sample = gr.Image()

                        master_params = [model_type, pitch, yaw, roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, source_ratio, sample_ratio, sample_parts, face_crop, restoration]
                        params = master_params + [img_ref]
                        opt_in_features_params = [img_sample]

                        basic_sliders = [pitch_basic, yaw_basic, roll_basic, blink_basic, eyebrow_basic, wink_basic, aaa_basic, eee_basic, woo_basic, smile_basic]
                        master_indices_basic = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12]
                        for slider, idx in zip(basic_sliders, master_indices_basic):
                            slider.change(
                                fn=lambda val, idx=idx: [val if i == idx else p.value for i, p in enumerate(master_params)],
                                inputs=[slider],
                                outputs=master_params
                            )

                        advanced_sliders = [pupil_x_adv, pupil_y_adv, source_ratio_adv, face_crop_adv, restoration_adv]
                        master_indices_adv = [7, 8, 13, 16, 17]
                        for slider, idx in zip(advanced_sliders, master_indices_adv):
                            slider.change(
                                fn=lambda val, idx=idx: [val if i == idx else p.value for i, p in enumerate(master_params)],
                                inputs=[slider],
                                outputs=master_params
                            )

                        for preset_btn in preset_buttons:
                            preset_btn.click(
                                fn=self.apply_preset,
                                inputs=[gr.Textbox(value=preset_btn.value, visible=False)] + params,
                                outputs=params
                            )

                        gr.on(
                            triggers=[param.change for param in master_params],
                            fn=self.inferencer.edit_expression,
                            inputs=params + opt_in_features_params,
                            outputs=img_out,
                            show_progress="minimal",
                            queue=True
                        )

                        btn_openfolder.click(
                            fn=lambda: self.open_folder(self.args.output_dir), inputs=None, outputs=None
                        )

                        btn_gen.click(
                            fn=self.inferencer.edit_expression,
                            inputs=params + opt_in_features_params,
                            outputs=img_out
                        )

                        # Connect the reset button
                        btn_reset.click(
                            fn=self.reset_to_default,
                            inputs=params,
                            outputs=params
                        )

                    with gr.TabItem(_("Saved Presets"), elem_classes="main-tab"):
                        with gr.Column(elem_classes="card"):
                            with gr.Row(elem_classes="card-header"):
                                gr.Markdown(_("Manage Your Custom Presets"))
                            with gr.Row(elem_classes="card-body"):
                                with gr.Column(scale=2):
                                    preset_name_input = gr.Textbox(label=_("Preset Name"))
                                    save_preset_btn = gr.Button(_("Save Current Settings as Preset"), elem_classes="btn-primary")
                                with gr.Column(scale=3):
                                    saved_presets_list = gr.Dataframe(
                                        headers=["Preset Name", "Date Created"],
                                        datatype=["str", "str"],
                                        col_count=(2, "fixed"),
                                        value=[["Happy (Custom)", "2025-03-29"], 
                                               ["Confused (Custom)", "2025-03-28"]],
                                        interactive=False
                                    )
                                    with gr.Row():
                                        load_preset_btn = gr.Button(_("Load Selected"), elem_classes="btn-secondary")
                                        delete_preset_btn = gr.Button(_("Delete Selected"), elem_classes="btn-secondary")

                with gr.Column(elem_classes="footer"):
                    gr.Markdown(_("Custom Emotion Generator • Made with ❤️"))

            gradio_launch_args = {
                "inbrowser": self.args.inbrowser,
                "share": self.args.share,
                "server_name": self.args.server_name,
                "server_port": self.args.server_port,
                "root_path": self.args.root_path,
                "auth": (self.args.username, self.args.password) if self.args.username and self.args.password else None,
            }
            self.app.queue(default_concurrency_limit=1).launch(**gradio_launch_args)

    @staticmethod
    def open_folder(folder_path: str):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            print(f"The directory path {folder_path} has been newly created.")
        if os.name == 'nt':  # Windows
            os.system(f"start {folder_path}")
        elif os.name == 'posix':  # macOS/Linux
            os.system(f"open {folder_path}" if "darwin" in os.sys.platform else f"xdg-open {folder_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--share', type=str2bool, default=False, nargs='?', const=True, help='Gradio share value')
    parser.add_argument('--inbrowser', type=str2bool, default=True, nargs='?', const=True,
                        help='Whether to automatically starts on the browser or not')
    parser.add_argument('--server_name', type=str, default=None, help='Gradio server host')
    parser.add_argument('--server_port', type=int, default=None, help='Gradio server port')
    parser.add_argument('--root_path', type=str, default=None, help='Gradio root path')
    parser.add_argument('--username', type=str, default=None, help='Gradio authentication username')
    parser.add_argument('--password', type=str, default=None, help='Gradio authentication password')
    parser.add_argument('--model_dir', type=str, default=MODELS_DIR,
                        help='Directory path of the LivePortrait models')
    parser.add_argument('--output_dir', type=str, default=OUTPUTS_DIR,
                        help='Directory path of the outputs')
    _args = parser.parse_args()

    app = App(args=_args)
    app.launch()