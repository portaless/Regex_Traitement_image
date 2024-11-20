import cv2
import pytesseract
import numpy as np
import mss
import pyperclip  # Pour gérer le presse-papiers

# Si nécessaire, indiquer le chemin de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\cportalier\Documents\Python_WP\TA\.venv\tesseract.exe'

# Variables globales pour la gestion de la zone de capture
zone_start = None
zone_end = None
drawing = False
cropped_image = None

# Fonction appelée par OpenCV quand un événement de souris se produit
def dessiner_rectangle(event, x, y, flags, param):
    global zone_start, zone_end, drawing, cropped_image

    if event == cv2.EVENT_LBUTTONDOWN:  # Clic gauche enfoncé
        drawing = True
        zone_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:  # Mouvement de la souris
        if drawing:
            image_temp = image_resized.copy()
            cv2.rectangle(image_temp, zone_start, (x, y), (0, 255, 0), 2)
            cv2.imshow("Image", image_temp)

    elif event == cv2.EVENT_LBUTTONUP:  # Clic gauche relâché
        drawing = False
        zone_end = (x, y)
        cv2.rectangle(image_resized, zone_start, zone_end, (0, 255, 0), 2)
        cv2.imshow("Image", image_resized)

        # Capturer la portion sélectionnée
        capturer_zone_selectionnee()

# Fonction pour capturer l'écran avec mss
def capture_ecran():
    with mss.mss() as sct:
        # Capturer le premier moniteur (entier) par défaut
        screenshot = np.array(sct.grab(sct.monitors[1]))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)  # Conversion en format OpenCV
        return screenshot

# Fonction pour capturer et découper la zone sélectionnée par l'utilisateur
def capturer_zone_selectionnee():
    global cropped_image, zone_start, zone_end

    if zone_start and zone_end:
        # Obtenir les coordonnées de la sélection
        x1, y1 = min(zone_start[0], zone_end[0]), min(zone_start[1], zone_end[1])
        x2, y2 = max(zone_start[0], zone_end[0]), max(zone_start[1], zone_end[1])

        # Découper l'image capturée à la zone sélectionnée
        cropped_image = image_resized[y1:y2, x1:x2]

        # Appliquer l'OCR à la zone découpée
        if cropped_image.size > 0:
            texte = pytesseract.image_to_string(cropped_image)
            print("Texte détecté dans la zone sélectionnée :")
            print(texte)

            # Copier le texte dans le presse-papiers
            pyperclip.copy(texte)
            print("Texte copié dans le presse-papiers.")

            # Afficher la zone sélectionnée
            cv2.imshow("Zone sélectionnée", cropped_image)

# Capture de l'écran actif
image = capture_ecran()

# Taille maximale de la fenêtre
max_width, max_height = 1920, 1080

# Redimensionner l'image pour ne pas dépasser les dimensions de l'écran
height, width = image.shape[:2]
ratio = min(max_width / width, max_height / height)
new_width = int(width * ratio)
new_height = int(height * ratio)
image_resized = cv2.resize(image, (new_width, new_height))

# Afficher l'image redimensionnée
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.imshow("Image", image_resized)

# Initialiser la capture des événements de souris
cv2.setMouseCallback("Image", dessiner_rectangle)

# Boucle principale pour la gestion des événements et affichage
while True:
    key = cv2.waitKey(1) & 0xFF

    # Appuyer sur 'q' pour quitter
    if key == ord('q'):
        break

cv2.destroyAllWindows()
