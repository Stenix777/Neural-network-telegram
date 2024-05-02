from .inline.admin_keyboards import gen_admin_links_kb, gen_admin_main_kb
from .inline.ais_keyboards import (gen_ai_types_kb, gen_img_model_kb,
                                   gen_main_video_kb, gen_text_models_kb,
                                   gen_text_roles_kb, gen_txt_settings_kb)
from .inline.article_keyboards import (gen_article_mode_kb,
                                       gen_article_search_kb,
                                       gen_edit_work_plan_kb)
from .inline.common_keyboards import gen_error_kb
from .inline.diploma_keyboards import (gen_confirm_start_work_kb,
                                       gen_diploma_struct_kb, gen_type_work_kb)
from .inline.faq_keyboards import (gen_back_faq_kb, gen_faq_finances_kb,
                                   gen_faq_finances_sub_kb, gen_faq_inline_kb,
                                   gen_faq_problems_kb, gen_faq_rec_kb,
                                   gen_main_faq_kb)
from .inline.midjourney_keyboards import gen_midjourney_kb
from .inline.payments_keyboards import (gen_confirm_premium_kb,
                                        gen_no_tokens_kb,
                                        gen_premium_cancel_kb, gen_premium_kb,
                                        gen_tokens_kb)
from .inline.profile_keyboards import gen_profile_kb
from .inline.services_keyboards import (gen_learning_kb, gen_other_services_kb,
                                        gen_services_back_kb, gen_services_kb,
                                        gen_working_kb)
from .inline.silero_keyboards import (gen_main_speaker_kb,
                                      gen_speaker_category_kb, gen_tts_kb)
from .reply.main_keyboard import main_kb
