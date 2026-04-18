import os
import shutil

src_root = r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets"
dest_root = r"c:\Tele_CRM\static\images\brand_logos"

files = [
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-7da59e37-c9dd-4aa4-a461-03c211a1c897.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-fd12b7cc-aa54-409b-af14-9088b2e28bbb.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-156b7822-3d8e-4a68-b17b-abf73c31f5a9.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-98957b53-c1e1-4edd-816a-c489e55229e3.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-a557ae29-56eb-40c6-b068-06dccb937fbc.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-7fb20a18-b709-48f2-9682-6280cb6242b2.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-6f6e79b3-8b56-4ed2-8ad9-ad3ea18de613.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-0fbd2157-2f4b-42b6-b67b-8e0e0933e692.png",
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-12ac2519-b9f9-4c89-90d2-ea20db2f_a1c7.png", # Wait, let me check the name again
    "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_mynest-log-1-e1644572796296-300x168-57405ca3-585e-4c54-a0c2-8a524c54287a.png"
]

# Correcting the name for 12ac2519 based on previous ls output:
# c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-12ac2519-b9f9-4c89-90d2-ea20db2fa1c7.png

files[8] = "c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-12ac2519-b9f9-4c89-90d2-ea20db2fa1c7.png"

for f in files:
    src = os.path.join(src_root, f)
    dest = os.path.join(dest_root, f)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"Copied {f}")
    else:
        print(f"Skipped {f} (not found)")
